from data.database import read_query, update_query, insert_query
from data.models import Tournament, Player, Match, MatchTournResponseMod, MatchResponseMod, SetMatchScoreMod, WinnerResponseMode, MatchesResponseMod
from common.validators import check_date
from services import user_service, tournaments_service
from common.validators import check_date, check_score, _MATCH_PHASES, _SORT_BY_VAL
from datetime import datetime, date
from common.exceptions import BadRequest
from fastapi import Response


# from services.tournaments_service import get_tournament_title_by_id <-- You can get it from get_tournament_by_id and
# then tournament.title


def create_next_phase(winner_ids: list[int],
                      current_phase: str,
                      tourn_id: int,
                      match_format: str | None = 'Time limited',
                      date: datetime | None = None) -> list[MatchTournResponseMod]:
    matches = []
    ind = find_next_phase(current_phase) - 1

    if ind < 0:
        raise BadRequest(f'Final is the last phase.')
    
    next_phase = _MATCH_PHASES[ind]

    players_names = get_players_names(winner_ids)

    n = len(winner_ids) // 2
    for _ in range(int(n)):
        match_id = insert_query('''INSERT INTO matches(format, date, tournament_id, match_phase)
                              VALUES(?,?,?,?)''', (match_format, date, tourn_id, next_phase))

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


def create_matches(tournament: Tournament, players: list[list[str]] | tuple) -> list[MatchTournResponseMod]:
    matches = []
    # Randomly assigned players that come like argument from create_tournament
    # = [['Player1', 'Player4'], ['Player2', 'Player3']]
    for index in range(len(players)):
        if tournament.scheme_format:  # We are taking each list in the list: [['Player1', 'Player4']]
            match_id = insert_query('''INSERT INTO matches(format, date, tournament_id, match_phase)
                              VALUES(?,?,?,?)''',
                                    (tournament.match_format, tournament.start_date, tournament.id,
                                     tournament.scheme_format))
        elif not tournament.scheme_format:
            match_id = insert_query('''INSERT INTO matches(format, date, tournament_id, match_phase)
                                          VALUES(?,?,?,?)''',
                                    (tournament.match_format, tournament.start_date, tournament.id,
                                     'League'))
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


def change_match_score(match_id: int, match_score: SetMatchScoreMod) -> None | WinnerResponseMode:
    pl_1_id = match_score.pl_1_id
    pl_2_id = match_score.pl_2_id
    pl_1_score = match_score.pl_1_score
    pl_2_score = match_score.pl_2_score
    tournament = tournaments_service.get_tournament_by_id(match_score.tourn_id)
    match_format, value = tournaments_service.separate_tournament_format(tournament)
    match = get_match_by_id(match_id)
    is_final = check_if_match_final(match_id)
    match_status = match_score.match_finished

    if not match_status:
        if match_format == 'Score Limited':
            if pl_1_score > value or pl_2_score > value:
        # Тука мача свършва ако са надминате ограниченията за резултата
                match_score.match_finished = True
        #       Имплемнтация за statistic
        elif match_format == 'Time Limited':
            if match.date + value > datetime.now(): # Shte go razgledam kak da se formatira i da gi sumira tochno
        #       Тука мача свършва ако са надминате ограниченията за резултата
                match_score.match_finished = True
        #       ako i dvete proverki minavat togava da vlizame v update_query
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
        
        if is_final:
            namee, countryy, clubb = list(get_player_name_club_country(pl_1_id)[0])
            tourn_name = get_tournament_title(match_score.tourn_id)[0][0]
            return WinnerResponseMode(name=namee,
                                      club=clubb,
                                      country=countryy,
                                      tournament_won=tourn_name)

    elif pl_1_score < pl_2_score:

        update_query('''UPDATE matches_has_players_profiles
                        SET score = ?, win = 0
                        WHERE matches_id = ? and player_profile_id = ?''', (pl_1_score, match_id, pl_1_id))
        update_query('''UPDATE matches_has_players_profiles
                        SET score = ?, win = 1
                        WHERE matches_id = ? and player_profile_id = ?''', (pl_2_score, match_id, pl_2_id))
        
        if is_final:
            namee, countryy, clubb = list(get_player_name_club_country(pl_2_id)[0])
            tourn_name = get_tournament_title(match_score.tourn_id)[0][0]
            return WinnerResponseMode(name=namee,
                                      club=clubb,
                                      country=countryy,
                                      tournament_won=tourn_name)
    else:
        raise ValueError('Мача e X, кво праим?')
    
    return Response(status_code=200, content='Score changed successfully')


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
        if not winner_id:
            raise BadRequest(f'Matches did not finished yet.')
        
        winners.append(winner_id[0][0])

    return winners[::-1]

def find_next_phase(current_fase: str) -> int:
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


def update_participants_for_matches(tournament, old_player, new_player):
    matches_ids = user_service.check_if_player_have_assigned_matches(tournament, old_player)
    if matches_ids:
        for match in matches_ids:
            match_id = match[0]
            update_query(
                "UPDATE matches_has_players_profiles SET player_profile_id = ? WHERE matches_id = ? AND "
                "player_profile_id = ?",
                (new_player.id, match_id, old_player.id))
        update_query(
            "UPDATE tournaments_has_players_profiles SET player_profile_id = ? WHERE tournament_id = ? AND "
            "player_profile_id = ?",
            (new_player.id, tournament.id, old_player.id))
        return True
    return False


def check_if_match_final(match_id: int) -> bool:

    return any(
        read_query(
            '''SELECT 1 FROM matches
            WHERE id = ? and match_phase = ?''', (match_id, 'final')))


def get_player_name_club_country(player_id: int):

    return read_query(
        '''SELECT full_name, country, club FROM players_profiles
        WHERE id = ?''', (player_id,))


def get_tournament_title(tourn_id: int):

    return read_query(
        '''SELECT title FROM tournaments
        WHERE id = ?''', (tourn_id,))


def get_all_matches(sort: str | None = None, sort_by: str | None = None) -> list[MatchesResponseMod]:

    if sort_by:

        if sort_by not in _SORT_BY_VAL:
            raise BadRequest(f'Cannot sort by: {sort_by}')
        
        sort_by = 'm.' + sort_by
        data = read_query(f'''SELECT m.id, full_name, mp.score, m.date, t.title FROM matches m
                                JOIN matches_has_players_profiles mp ON m.id = mp.matches_id
                                JOIN tournaments t ON m.tournament_id = t.id
                                JOIN players_profiles pp ON pp.id = mp.player_profile_id
                                ORDER BY {sort_by} {sort}''')
    else:
        data = read_query('''SELECT m.id, full_name, score, date, t.title FROM matches m
                                    JOIN matches_has_players_profiles mp ON m.id = mp.matches_id
                                    JOIN tournaments t ON m.tournament_id = t.id
                                    JOIN players_profiles pp ON pp.id = mp.player_profile_id''')
    
    return packaging_for_all_matches(data)


def set_match_date(match_id: int, m_date: datetime):
    
    ans = update_query('''UPDATE matches SET date = ?
                 WHERE id = ?''',(m_date, match_id))
    
    if not ans:
        raise BadRequest(f'Something went wrong.')
    
    return Response(status_code=200, content=f'Match #{match_id} date set to: {m_date}')


def paginating_matches(page: int, 
                       page_size: int | None = 2, 
                       sort: str | None = None, 
                       sort_by: str | None = None):

    if page <= 0:
        return BadRequest('Page must be equal to or higher than 1.')
    page = (int(page)-1) * int(page_size)

    if sort_by:

        data = read_query(f'''WITH pag AS                               
                                    (SELECT m.id, m.format, m.date, m.tournament_id, m.match_phase 
                                        FROM matches m
                                        ORDER BY {sort_by} {sort}
                                        OFFSET {page} ROWS FETCH NEXT {page_size} ROWS ONLY)
                                SELECT pa.id, pp.full_name, mp.score, m.date, t.title FROM pag pa
                                JOIN matches m ON m.id = pa.id
                                JOIN matches_has_players_profiles mp ON m.id = mp.matches_id
                                JOIN tournaments t ON m.tournament_id = t.id
                                JOIN players_profiles pp ON pp.id = mp.player_profile_id''')
    else:
        data = read_query(f'''WITH pag AS                               
                                    (SELECT m.id, m.format, m.date, m.tournament_id, m.match_phase 
                                        FROM matches m
                                        OFFSET {page} ROWS FETCH NEXT {page_size} ROWS ONLY)
                                SELECT pa.id, pp.full_name, mp.score, m.date, t.title FROM pag pa
                                JOIN matches m ON m.id = pa.id
                                JOIN matches_has_players_profiles mp ON m.id = mp.matches_id
                                JOIN tournaments t ON m.tournament_id = t.id
                                JOIN players_profiles pp ON pp.id = mp.player_profile_id''')
    
    return packaging_for_all_matches(data)


def packaging_for_all_matches(data: list) -> list[MatchesResponseMod]:

    all_matches = []
    index = 0
    while index < (len(data) - 1):
        player_1_data = data[index]
        player_2_data = data[index + 1]
        match_id = player_1_data[0]
        match_date = player_1_data[-2]
        tourn_title = player_1_data[-1]

        pl_1_name = player_1_data[1]
        pl_1_score = str(player_1_data[2])
        pl_2_name = player_2_data[1]
        pl_2_score = str(player_2_data[2])

        names_and_scores = pl_1_name + ' ' + pl_1_score + ' - ' + pl_2_score + ' ' + pl_2_name

        match_resp = MatchesResponseMod(
            match_id=match_id,
            score=names_and_scores,
            match_date=match_date,
            tournament_title=tourn_title)
        
        
        all_matches.append(match_resp)

        index += 2
    
    return all_matches
