import random

from data.database import read_query, update_query, insert_query
from data.models import Tournament, Player


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


def generate_knockout_scheme(players):
    scheme_format = ''
    players_count = len(players)
    if players_count % 2 != 0:
        return None
    if players_count == 2:
        scheme_format = 'final'
    elif players_count == 4:
        scheme_format = 'semi-final'
    elif players_count == 6:
        scheme_format = 'quarterfinals'
    elif players_count == 8:
        scheme_format = 'eight-finals'
    elif players_count > 8:
        return 'Poveche nedavam'
    if players_count > 2:
        first_match_player1 = random.choice(players)
        players.remove(first_match_player1)
        first_match_player2 = random.choice(players)
        players.remove(first_match_player2)
        second_match_player1 = random.choice(players)
        players.remove(second_match_player1)
        second_match_player2 = random.choice(players)
        players.remove(second_match_player2)
        first_match = {'first_player': first_match_player1, 'second_player': first_match_player2}
        second_match = {'first_player': second_match_player1, 'second_player': second_match_player2}
    else:
        last_match_player1 = random.choice(players)
        last_match_player2 = random.choice(players)
        last_match = {'first_player': last_match_player1, 'second_player': last_match_player2}
        return scheme_format, last_match
    return scheme_format, first_match, second_match

