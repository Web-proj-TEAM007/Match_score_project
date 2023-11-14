from data.database import read_query, update_query, insert_query
from data.models import Tournament, Player, Match, MatchTournResponseMod, MatchResponseMod, SetMatchScoreMod
from common.validators import check_date


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

# matches_has_players_profiles

def get_match_by_id(match_id: int):

    data = read_query('''SELECT m.matches_id, t.title, pl.full_name, m.score, mt.date 
                      FROM matches_has_players_profiles m, players_profiles pl
                            JOIN matches mt ON mt.id = ?
                            JOIN tournaments t ON t.id = mt.tournament_id
                            WHERE m.matches_id = ? and m.player_profile_id = pl.id''', (match_id, match_id))

    player_one = data[0][2] + ': ' + str(data[0][-2])
    player_two = data[1][2] + ': ' + str(data[0][-2])
    datee = data[0][-1]
    tourn_title = data[0][1]
    datee = check_date(datee)

    d_match = MatchResponseMod(id=match_id, 
                               tournament_title=tourn_title, 
                               player_1=player_one, 
                               player_2=player_two, 
                               date=datee)

    return d_match


def create_match_v2(tournament: Tournament, players: list[list[str]]) -> list[MatchTournResponseMod]:
    matches = []
    # Randomly assigned players that come like argument from create_tournament
    # = [['Player1', 'Player4'], ['Player2', 'Player3']]
    for index in range(len(players)):  # We are taking each separate list in the list: ['Player1', 'Player4']
        match_id = insert_query('''INSERT INTO matches(format, date, tournament_id, match_fase)
                              VALUES(?,?,?)''', (tournament.match_format, tournament.start_date, tournament.id, tournament.scheme_format))
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


def change_match_score(match_id: int, match_score: SetMatchScoreMod) -> None:
    
    pl_1_id = match_score.pl_1_id
    pl_2_id = match_score.pl_2_id
    pl_1_score = match_score.pl_1_score
    pl_2_score = match_score.pl_2_score

    match_status = match_score.match_finished


    if not match_status:

        update_query('''UPDATE matches_has_players_profiles
                        SET score = ?
                        WHERE matches_id = ? and player_profile_id = ?''',(pl_1_score, match_id, pl_1_id))
        update_query('''UPDATE matches_has_players_profiles
                        SET score = ?
                        WHERE matches_id = ? and player_profile_id = ?''',(pl_2_score, match_id, pl_2_id))
    elif pl_1_score > pl_2_score:

        update_query('''UPDATE matches_has_players_profiles
                        SET score = ?, win = 1
                        WHERE matches_id = ? and player_profile_id = ?''',(pl_1_score, match_id, pl_1_id))
        update_query('''UPDATE matches_has_players_profiles
                        SET score = ?, win = 0
                        WHERE matches_id = ? and player_profile_id = ?''',(pl_2_score, match_id, pl_2_id))
    elif pl_1_score < pl_2_score:

        update_query('''UPDATE matches_has_players_profiles
                        SET score = ?, win = 0
                        WHERE matches_id = ? and player_profile_id = ?''',(pl_1_score, match_id, pl_1_id))
        update_query('''UPDATE matches_has_players_profiles
                        SET score = ?, win = 1
                        WHERE matches_id = ? and player_profile_id = ?''',(pl_2_score, match_id, pl_2_id))
    else:
        raise ValueError('Мача e X, кво праим?')


def get_matches_for_tournament(tournament_id: int):
    # ---- To Shahin: Will need this function to properly return tournaments
    data = read_query('''SELECT id, format, date, tournament_id FROM matches WHERE tournament_id = ?''', (tournament_id,))

    return (Match.from_query_result(*row) for row in data)


def match_exists(match_id: int) -> bool:
    return any(
        read_query(
            '''SELECT 1 FROM matches WHERE id = ?''',
            (match_id,)))

def check_match_finished(match_id: int) -> bool:

    return any(
        read_query(
            '''SELECT 1 FROM matches_has_players_profiles 
	WHERE matches_id = ? and win is not Null''', (match_id,)))