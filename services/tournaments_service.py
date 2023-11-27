from authentication.jwt_bearer import JWTBearer
from data.database import read_query, update_query, insert_query
from data.models import Tournament, Player, TournamentCreateModel, UpdateParticipantModel, Match, NewPhase
import random
from common.validators import tournament_format_validator
from common.exceptions import BadRequest, NotFound
from fastapi import Response
from services import user_service, match_service
import itertools
from datetime import date
from common.validators import _MATCH_PHASES


def get_all_tournaments(title, tour_format):
    query = "SELECT id, title, format, prize, start_date, winner FROM tournaments"
    params = []
    where_clauses = []
    if title:
        where_clauses.append("title = ?")
        params.append(title)
    if tour_format:
        where_clauses.append("format = ?")
        params.append(tournament_format_validator(tour_format))
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    data = read_query(query, params)
    tournaments = [Tournament.from_query_result(*row) for row in data]
    return tournaments


def get_tournament_by_id(tour_id: int) -> Tournament:
    data = read_query('SELECT id, title, format, prize, start_date, winner FROM tournaments WHERE id = ?', (tour_id,))
    tournament = next((Tournament.from_query_result(*row) for row in data), None)
    if tournament:
        tournament.participants = get_tournament_participants(tournament.id)
        tournament.matches = match_service.get_matches_for_tournament(tournament.id)
        tournament.match_format = tournament.matches[-1].format
    return tournament


def create_tournament(tournament: TournamentCreateModel) -> Tournament:
    generated_id = insert_query("INSERT INTO tournaments (format, title, prize, start_date) VALUES (?, ?, ?, ?)",
                                (tournament.tour_format, tournament.title,
                                 tournament.prize, tournament.start_date))
    return Tournament(
        id=generated_id,
        title=tournament.title,
        tour_format=tournament.tour_format,
        prize=tournament.prize,
        match_format=tournament.match_format,
        participants=tournament.participants,
        start_date=tournament.start_date
    )


# ------ this will be moved to a player_service most likely but for now is here to test tournaments get by id -----
def get_tournament_participants(tour_id: int) -> list[Player]:
    data = read_query('''
        SELECT players_profiles.id, players_profiles.full_name, players_profiles.country, players_profiles.club
        FROM tournaments_has_players_profiles
        JOIN players_profiles ON tournaments_has_players_profiles.player_profile_id = players_profiles.id
        WHERE tournaments_has_players_profiles.tournament_id = ?
    ''', (tour_id,))
    participants = [Player.from_query_result(*row) for row in data]
    return participants


def manage_tournament(tournament, new_date: date | None, change_participants: UpdateParticipantModel | None):
    response = []
    if new_date:
        old_date = tournament.start_date
        update_query("UPDATE tournaments SET start_date = ? WHERE id = ?", (new_date, tournament.id))
        response.append(Response(status_code=200, content=f'Successfully changed tournament start date from '
                                                          f'{old_date} to {new_date}'))
    if change_participants:
        new_player = user_service.get_player_profile_by_fullname(change_participants.new_player)
        old_player = user_service.get_player_profile_by_fullname(change_participants.old_player)
        tournament.participants.remove(old_player)
        tournament.participants.append(new_player)
        if match_service.update_participants_for_matches(tournament, old_player, new_player):
            response.append(Response(status_code=200, content=f'Successfully changed tournament participant: '
                                                              f'{old_player.full_name} with {new_player.full_name} '
                                                              f'and updated upcoming matches with the new player'))
        else:
            response.append(Response(status_code=200, content=f'Successfully changed tournament participant: '
                                                              f'{old_player.full_name} with {new_player.full_name}, '
                                                              f'no matches are updated'))
    return response


def generate_knockout_schema(players):
    match_players = []
    players_count = len(players)
    if not players_count:
        return match_players
    if players_count % 2 != 0:
        raise BadRequest('Players must be even numbers')
    first_match_player1 = random.choice(players)
    players.remove(first_match_player1)
    first_match_player2 = random.choice(players)
    players.remove(first_match_player2)
    match_players.append([first_match_player1, first_match_player2])
    match_players.extend(generate_knockout_schema(players))
    return match_players


# output : [['Player1', 'Player4'], ['Player2', 'Player3']]


def generate_league_schema(players):
    player_pairs = list(itertools.combinations(players, 2))
    match_schema = [[pair[0], pair[1]] for pair in player_pairs]
    return match_schema


def get_scheme_format(players_count):
    if players_count == 2:
        return 'final'
    elif players_count == 4:
        return 'semi-final'
    elif players_count == 8:
        return 'quarterfinals'
    elif players_count == 16:
        return 'eight-finals'
    elif players_count % 2 == 1:
        raise BadRequest('Players number must be 2,4,8 or 16.')
    elif players_count > 16:
        raise BadRequest('Too many players, max is 16.')


def tournament_exists(tour_title: str) -> bool:
    return any(read_query('''SELECT 1 FROM tournaments WHERE title = ?''', (tour_title,)))


def tournament_exists_by_id(tournament_id: int) -> bool:
    return any(
        read_query(
            '''SELECT 1 FROM tournaments WHERE id = ?''', (tournament_id,)))


def insert_participants_into_tournament(player_profiles_id: list[int], tournament_id):
    for player_id in player_profiles_id:
        insert_query('''INSERT INTO tournaments_has_players_profiles(tournament_id, player_profile_id)
                            VALUES(?,?)''', (tournament_id, player_id))


def insert_tournament_winner(tournament: Tournament, player: Player) -> None:
    update_query("UPDATE tournaments SET winner = ? WHERE id = ?", (player.full_name, tournament.id))


def check_if_league_is_over(tournament_id: int) -> int | None:
    # League is considered as over when all matches have been played
    total_matches = match_service.get_matches_for_tournament(tournament_id)
    matches_played = match_service.get_all_finished_league_matches(tournament_id)
    if len(matches_played) == len(total_matches):
        winner_id = match_service.get_league_winner(tournament_id)
        return winner_id
    return None


def check_if_knockout_phase_is_over(tournament: Tournament):
    matches_phases = [match.match_phase for match in tournament.matches]
    last_phase = matches_phases[-1] if matches_phases else None
    matches_played = match_service.get_all_finished_knockout_matches(tournament.id, match_phase=last_phase)
    total_matches = match_service.get_matches_with_exact_phase(tournament.id, match_phase=last_phase)
    if len(matches_played) == len(total_matches):
        return True, last_phase
    return False


def move_phase(tournament_id: int, current_phase: str):
    # user = get_user_from_token(token)
    # if user.user_role != 'Director':
    #     raise Unauthorized(content='Only directors can change tournament phase')
    tournament = get_tournament_by_id(tournament_id)
    # if tournament.tour_format == 'League':
    #     raise BadRequest(detail='Only knockout tournaments can change phases')
    if current_phase not in _MATCH_PHASES:
        raise BadRequest('Invalid phase.')
    match_ids = match_service.get_matches_ids(tournament.id, current_phase)
    if not match_ids:
        raise NotFound(detail=f'No available matches with phase: {current_phase}')
    winners_reversed = match_service.get_winners_ids(match_ids)
    return match_service.create_next_phase(winners_reversed, current_phase, tournament)