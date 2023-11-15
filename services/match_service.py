from data.database import read_query, update_query, insert_query
from data.models import Tournament, Player, Match, MatchTournResponseMod, MatchResponseMod, SetMatchScoreMod
from common.validators import check_date
from services import user_service
from common.validators import check_date, check_score, _MATCH_PHASES
from datetime import datetime
from common.exceptions import BadRequest


# from services.tournaments_service import get_tournament_title_by_id <-- You can get it from get_tournament_by_id and
# then tournament.title


def create_next_fase(winner_ids: list[int], 
                     current_fase: str, 
                     tourn_id: int,
                     match_format: str | None = 'Time limited', 
                     date: datetime | None = None) -> list[MatchTournResponseMod]:

    matches = []
    next_fase = _MATCH_PHASES[find_next_fase(current_fase) - 1]

    if next_fase < 0:
        raise BadRequest(f'Final is the last phase.')

    players_names = get_players_names(winner_ids)

    n = len(winner_ids) // 2
    for _ in range(int(n)):
        match_id = insert_query('''INSERT INTO matches(format, date, tournament_id, match_phase)
                              VALUES(?,?,?,?)''',(match_format, date, tourn_id, next_fase))

        player_1 = winner_ids[-1]
        player_2 = winner_ids[-2]
        winner_ids.pop()
        winner_ids.pop()

        insert_query('''INSERT INTO matches_has_players_profiles(matches_id, player_profile_id, score)
                    VALUES(?,?,?)''', (match_id, player_1, 0))
        insert_query('''INSERT INTO matches_has_players_profiles(matches_id, player_profile_id, score)
                    VALUES(?,?,?)''', (match_id, player_2, 0))

        player_1_name = players_names[-1]
        player_2_name = players_names[-2]
        players_names.pop()
        players_names.pop()
        this_match = MatchTournResponseMod(id=match_id,
                                           player_1=player_1_name,
                                           player_2=player_2_name,
                                           date='Not set yet')
        matches.append(this_match)

    return matches

# matches_has_players_profiles

def get_match_by_id(match_id: int):
    data = read_query('''SELECT m.matches_id, t.title, pl.full_name, m.score, mt.date, mt.match_phase 
                      FROM matches_has_players_profiles m, players_profiles pl
                            JOIN matches mt ON mt.id = ?
                            JOIN tournaments t ON t.id = mt.tournament_id
                            WHERE m.matches_id = ? and m.player_profile_id = pl.id''', (match_id, match_id))

    player_one = data[0][2] + ': ' + str(check_score(data[0][-3]))
    player_two = data[1][2] + ': ' + str(check_score(data[0][-3]))
    datee = data[0][-2]
    tourn_title = data[0][1]
    match_f = data[0][-1]
    datee = check_date(datee)

    d_match = MatchResponseMod(id=match_id, 
                               tournament_title=tourn_title, 
                               player_1=player_one, 
                               player_2=player_two, 
                               date=datee,
                               match_fase=match_f)

    return d_match


def create_match_v2(tournament: Tournament, players: list[list[str]]) -> list[MatchTournResponseMod]:
    matches = []
    # Randomly assigned players that come like argument from create_tournament
    # = [['Player1', 'Player4'], ['Player2', 'Player3']]
    for index in range(len(players)):  # We are taking each separate list in the list: ['Player1', 'Player4']
        match_id = insert_query('''INSERT INTO matches(format, date, tournament_id, match_phase)
                              VALUES(?,?,?,?)''', 
                              (tournament.match_format, tournament.start_date, tournament.id, tournament.scheme_format))
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
                        WHERE matches_id = ? and player_profile_id = ?''', (pl_1_score, match_id, pl_1_id))
        update_query('''UPDATE matches_has_players_profiles
                        SET score = ?
                        WHERE matches_id = ? and player_profile_id = ?''', (pl_2_score, match_id, pl_2_id))
    elif pl_1_score > pl_2_score:

        update_query('''UPDATE matches_has_players_profiles
                        SET score = ?, win = 1
                        WHERE matches_id = ? and player_profile_id = ?''', (pl_1_score, match_id, pl_1_id))
        update_query('''UPDATE matches_has_players_profiles
                        SET score = ?, win = 0
                        WHERE matches_id = ? and player_profile_id = ?''', (pl_2_score, match_id, pl_2_id))
    elif pl_1_score < pl_2_score:

        update_query('''UPDATE matches_has_players_profiles
                        SET score = ?, win = 0
                        WHERE matches_id = ? and player_profile_id = ?''', (pl_1_score, match_id, pl_1_id))
        update_query('''UPDATE matches_has_players_profiles
                        SET score = ?, win = 1
                        WHERE matches_id = ? and player_profile_id = ?''', (pl_2_score, match_id, pl_2_id))
    else:
        raise ValueError('Мача e X, кво праим?')


def get_matches_for_tournament(tournament_id: int):
    # ---- To Shahin: Will need this function to properly return tournaments
    data = read_query('''SELECT * FROM matches WHERE tournament_id = ?''', (tournament_id,))

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

def get_matches_ids(tourn_id: int, match_fase: str) -> list[int]:

    match_ids = read_query('''SELECT id FROM matches 
                      WHERE tournament_id = ? and match_phase = ?''', 
                      (tourn_id, match_fase.lower()))

    return sorted(match_ids)

def get_winners_ids(match_ids: list[int]) -> list[str]:

    winners = []
    for id in match_ids:
        winner_id = read_query('''SELECT mpp.player_profile_id 
                                FROM matches_has_players_profiles mpp
                                WHERE mpp.matches_id = ? and mpp.win = 1''', (id[0],))
        winners.append(winner_id[0][0])

    return winners[::-1]

def find_next_fase(current_fase: str) -> int:

    for index, fase in enumerate(_MATCH_PHASES):
        if current_fase == fase:
            return index

def get_players_names(players_ids: list[int]) -> list[str]:

    players_names = []
    for id in players_ids:
        data = read_query('''SELECT full_name FROM players_profiles
                        WHERE id = ?''', (id,))
        players_names.append(data[0][0])
    return players_names

def check_player_in_match(player_id: int, match_id: int) -> bool:

    return any(
        read_query(
            '''SELECT 1 FROM matches_has_players_profiles
            WHERE matches_id = ? and player_profile_id = ?''',
            (match_id, player_id)))

# matches_has_players_profiles


def update_participants_for_matches(tournament, old_player, new_player):
    matches_ids = user_service.check_if_player_have_assigned_matches(tournament, old_player)
    if matches_ids:
        matches = [get_match_by_id(match_id) for match_id in matches_ids]
        for match in matches:
            update_query(
                "UPDATE matches_has_players_profiles SET player_profile_id = ? WHERE matches_id = ? AND "
                "player_profile_id = ?",
                new_player.id, match.id, old_player.id)
        return True
    return False