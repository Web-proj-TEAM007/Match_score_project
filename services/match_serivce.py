from data.database import read_query, update_query, insert_query
from data.models import Tournament, Player


def create_match(match):
    date, match_format, game_format = match
    if game_format == "Time limited":
        generated_id = insert_query("INSERT INTO matches(date, format, score_limit)"
                                    " values(?, ?, ?)",
                                    (date, match_format, game_format))
    elif game_format == "Score limited":
        generated_id = insert_query("INSERT INTO matches(date, format, score_limit)"
                                    " values(?, ?, ?)",
                                    (date, match_format, game_format))
    match.id = generated_id
    return match
