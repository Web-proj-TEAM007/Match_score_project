from data.database import read_query, update_query, insert_query
from data.models import Tournament, Player, Match, MatchTournResponseMod


# from services.tournaments_service import get_tournament_title_by_id <-- You can get it from get_tournament_by_id and
# then tournament.title

# class Tournament(BaseModel):
#     id: Optional[int] = None
#     title: str
#     tour_format: str
#     prize: int
#     schema: str | None = None
#     match_format: str | None = None
#     participants: list[str] | None = None
#     matches: Optional[Match] | None = None
#     start_date: Optional[datetime] = None

# class Match(BaseModel):
#     id: int | None = None
#     format: str
#     date: datetime | str = 'not set yet'
#     tourn_id: int

# needed: format, date, tourn_id
# def create_match(tournament: Tournament) -> list[MatchTournResponseMod]:
#
#     matches = []
#     participants = tournament.participants[::-1] # G: Защо обръщаш листа?
#     players_ids = get_participants_ids(participants)
#     n = len(players_ids) // 2
#     for _ in range(int(n)):
#         match_id = insert_query('''INSERT INTO matches(format, date, tournament_id)
#                               VALUES(?,?,?)''',(tournament.match_format, tournament.start_date, tournament.id))
#
#         player_1 = players_ids[-1]
#         player_2 = players_ids[-2]
#         players_ids.pop()
#         players_ids.pop()
#
#         insert_query('''INSERT INTO matches_has_players_profiles(matches_id, player_profile_id, score)
#                     VALUES(?,?,?)''', (match_id, player_1, 0))
#         insert_query('''INSERT INTO matches_has_players_profiles(matches_id, player_profile_id, score)
#                     VALUES(?,?,?)''', (match_id, player_2, 0))
#
#         player_1_name = participants[-1]
#         player_2_name = participants[-2]
#         participants.pop()
#         participants.pop()
#         this_match = MatchTournResponseMod(id=match_id,
#                                            player_1=player_1_name,
#                                            player_2=player_2_name,
#                                            date='Not set yet')
#         matches.append(this_match)
#
#     return matches


def create_match_v2(tournament: Tournament, players: list[list[str]]) -> list[MatchTournResponseMod]:
    matches = []
    # Randomly assigned players that come like argument from create_tournament
    # = [['Player1', 'Player4'], ['Player2', 'Player3']]
    for index in range(len(players)):  # We are taking each separate list in the list: ['Player1', 'Player4']
        match_id = insert_query('''INSERT INTO matches(format, date, tournament_id)
                              VALUES(?,?,?)''', (tournament.match_format, tournament.start_date, tournament.id))
        player1, player2 = players[index]  # eg. 'Player1', 'Player4'
        player1_id, player2_id = get_participants_ids(players[index])  # getting the ids
        insert_query('''INSERT INTO matches_has_players_profiles(matches_id, player_profile_id, score)
                    VALUES(?,?,?)''', (match_id, player1_id, 0))
        insert_query('''INSERT INTO matches_has_players_profiles(matches_id, player_profile_id, score)
                    VALUES(?,?,?)''', (match_id, player2_id, 0))
        this_match = MatchTournResponseMod(id=match_id,
                                           player_1=player1,
                                           player_2=player2,
                                           date='Not set yet')
        matches.append(this_match)
    return matches


def get_participants_ids(participants: list[str]) -> list[int]:
    players_ids = []
    for player in participants:
        data = read_query('''SELECT id FROM players_profiles
                        WHERE full_name = ?''', (player,))
        players_ids.append(data[0][0])
    return players_ids


def get_matches_for_tournament(tournament_id: int):
    # ---- To Shahin: Will need this function to properly return tournaments
    data = read_query('''SELECT * FROM matches WHERE tournament_id = ?''', (tournament_id,))

    return (Match.from_query_result(*row) for row in data)


def match_exists(match_id: int) -> bool:
    return any(
        read_query(
            '''SELECT 1 FROM matches WHERE id = ?''',
            (match_id,)))
