from data.database import read_query, update_query, insert_query
from data.models import Tournament, Player, Match


# from services.tournaments_service import get_tournament_title_by_id <-- You can get it from get_tournament_by_id and
# then tournament.title

# class Match(BaseModel):
#     id: int | None = None
#     format: str
#     date: datetime | str = 'not set yet'
#     tourn_id: int

# needed: format, date, tourn_id
def create_match(match: Match) -> Match:
    generated_id = insert_query('''INSERT INTO matches(format, date, tournament_id) VALUES(?,?,?)''',
                                (match.format, match.date, match.tourn_id))
    
    match.id = generated_id
    return match


def insert_players_into_matches(match_id: int, player1_id: int, player2_id: int):
    
    insert_query('''INSERT INTO matches_has_players_profiles(matches_id, player_profile_id, score)
                 VALUES(?,?,?)'''(match_id, player1_id, player2_id))
    

def get_matches_for_tournament(tournament_id: int):
    # ---- To Shahin: Will need this function to properly return tournaments
    data = read_query('''SELECT * FROM matches WHERE tournament_id = ?''', (tournament_id,))

    return (Match.from_query_result(*row) for row in data)


def match_exists(match_id: int) -> bool:
    return any(
        read_query(
            '''SELECT 1 FROM matches WHERE id = ?''',
            (match_id,)))
