from data.database import read_query, update_query, insert_query
from data.models import Tournament, Player, Match
from services.tournaments_service import get_tournament_title_by_id


# needed: format, date, tourn_id
def create_match(match: Match) -> Match:

    generated_id = insert_query('''INSERT INTO matches(format, date, tournament_id)
                                    VALUES(?,?,?)'''(match.format, match.date, match.tourn_id))

    match.id = generated_id
    return match


def get_matches_for_tournament(tournament_id: int):
    # ---- To Shahin: Will need this function to properly return tournaments
    data = read_query('''SELECT * FROM matches WHERE tournament_id = ?''', (tournament_id,))
    
    return (Match.from_query_result(*row) for row in data)

def match_exists(match_id: int) -> bool:

    return any(
        read_query(
            '''SELECT 1 FROM matches WHERE id = ?''', 
            (match_id,)))