from data.database import read_query, update_query, insert_query
from data.models import Tournament, Player, TournamentCreateModel, UpdateParticipantModel
import random
from common.validators import tournament_format_validator
from common.exceptions import BadRequest
from fastapi import Response
from services import user_service, match_service
import itertools
from datetime import date


def get_all_tournaments(title, tour_format):
    query = "SELECT id, title, format, prize FROM tournaments"
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


def get_tournament_by_id(tour_id: int):
    data = read_query('SELECT id, title, format, prize FROM tournaments WHERE id = ?', (tour_id,))
    tournament = next((Tournament.from_query_result(*row) for row in data), None)
    tournament.participants = get_tournament_participants(tournament.id)
    # if tournament.scheme_format
    # tournament.scheme_format = get_scheme_format(len(get_tournament_participants(tournament.id)))
    return tournament


def create_tournament(tournament: TournamentCreateModel) -> Tournament:
    generated_id = insert_query("INSERT INTO tournaments (format, title, prize) VALUES (?, ?, ?)",
                                (tournament.tour_format, tournament.title, tournament.prize))
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
        pass
        # Maybe we will need tournament start_date column in the DB
        # old_date = tournament.start_date
        # update_query("UPDATE tournaments SET start_date = ? WHERE id = ?", (new_date, tournament.id))
        # response.append(Response(status_code=200, content=f'Successfully changed tournament start date from '
        #                                                   f'{old_date} to {new_date}'))
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


def get_tournament_start_date(tournament):
    matches = match_service.get_matches_for_tournament(tournament.id)
    result = matches.sorted(key=lambda x: x.date, reverse=True)
    first_match_start_date = result[0]
    return first_match_start_date


def separate_tournament_format(tournament):
    # 'Time Limited: 60 minutes'
    value = [char for char in tournament.match_format if char.isdigit()]
    match_format = tournament.match_format[:":"]
    if not value:
        raise BadRequest('Something went wrong')
    return match_format, value
