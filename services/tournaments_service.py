from data.database import read_query, update_query, insert_query
from data.models import Tournament, Player
import random


def get_all_tournaments(title, tour_format):
    query = "SELECT id, title, format, prize FROM tournaments"
    params = []
    where_clauses = []
    if title:
        where_clauses.append("title = ?")
        params.append(title)
    if tour_format:
        where_clauses.append("format = ?")
        params.append(tour_format)
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    data = read_query(query, params)
    tournaments = [Tournament.from_query_result(*row) for row in data]
    return tournaments


def get_tournament_by_id(tour_id):
    data = read_query('SELECT * FROM tournaments WHERE id = ?', (tour_id,))
    tournament = next((Tournament.from_query_result(*row) for row in data), None)
    return tournament


# ------ this will be moved to a player_service most likely but for now is here to test tournaments get by id -----
def get_tournament_participants(tour_id):
    data = read_query('SELECT player_profile_id FROM tournaments_has_players_profile '
                      'WHERE tournament_id = ?', (tour_id,))
    participants = ((Player.from_query_result(*row) for row in data), None)
    return participants


def manage_event(tournament, new_date, change_participants):
    if new_date:
        # maybe start_date of the tournament need to be added to the db
        #   update_query("UPDATE tournaments SET start_date = ? WHERE id = ?", new_date, tournament.id)
        # IMPORTANT: after we change the tournament date make sure to move match date if needed
        tournament.start_date = new_date
    if change_participants:
        old, new = change_participants
        date = update_query(
            "UPDATE tournaments_has_player_profiles SET player_profile_id = ? WHERE tournament_id = ? "
            "AND player_profile_id = ?",
            new.id, tournament.id, old.id
        )


def generate_game_schema(players):
    match_players = []
    players_count = len(players)
    if players_count == 0:
        return match_players
    if players_count % 2 != 0:
        raise ValueError('Players must be even numbers')
    if players_count == 2:
        return 'final', {'first_player': players[0], 'second_player': players[1]}
    first_match_player1 = random.choice(players)
    players.remove(first_match_player1)
    first_match_player2 = random.choice(players)
    players.remove(first_match_player2)
    second_match_player1 = random.choice(players)
    players.remove(second_match_player1)
    second_match_player2 = random.choice(players)
    players.remove(second_match_player2)
    match_players.append({'first_player': first_match_player1, 'second_player': first_match_player2})
    match_players.append({'first_player': first_match_player1, 'second_player': first_match_player2})
    match_players.extend(generate_game_schema(players))
    return match_players


def get_scheme_format(players_count):
    if players_count == 4:
        return 'semi-final'
    elif players_count == 6:
        return 'quarterfinals'
    elif players_count == 8:
        return 'eight-finals'
    else:
        return 'Poveche nedavam'
