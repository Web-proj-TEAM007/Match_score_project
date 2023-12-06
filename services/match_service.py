from data.database import read_query, update_query, insert_query
from data.models import Tournament, Match, MatchTournResponseMod, MatchResponseMod, SetMatchScoreMod, \
    WinnerResponseMode, MatchesResponseMod
from services import user_service, tournaments_service, player_service
from common.validators import check_date, check_score, _MATCH_PHASES, _SORT_BY_VAL, time_limit_validator
from datetime import datetime
from common.exceptions import BadRequest
from fastapi import Response


# from services.tournaments_service import get_tournament_title_by_id <-- You can get it from get_tournament_by_id and
# then tournament.title


def create_next_phase(winner_ids: list[int],
                      current_phase: str,
                      tournament: Tournament,
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
                              VALUES(?,?,?,?)''', (tournament.match_format, date, tournament.id, next_phase))

        player_1, player_2 = winner_ids.pop(), winner_ids.pop()

        insert_query('''INSERT INTO matches_has_players_profiles(matches_id, player_profile_id, score)
                    VALUES(?,?,?)''', (match_id, player_1, 0))
        insert_query('''INSERT INTO matches_has_players_profiles(matches_id, player_profile_id, score)
                    VALUES(?,?,?)''', (match_id, player_2, 0))

        player_1_name, player_2_name = players_names.pop(), players_names.pop()
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
    player_two = data[1][2] + ': ' + str(check_score(data[1][-3]))
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


def get_match_by_id_v2(match_id: int) -> Match:
    data = read_query('SELECT * FROM matches WHERE id = ?', (match_id,))
    match = next((Match.from_query_result(*row) for row in data), None)
    return match


def create_matches(tournament: Tournament, players: list[list[str]] | tuple) -> list[MatchTournResponseMod]:
    matches = []
    # Randomly assigned players that come like argument from create_tournament
    # = [['Player1', 'Player4'], ['Player2', 'Player3']]
    for index in range(len(players)):  # We are taking each list in the list: [['Player1', 'Player4']]
        match_id = insert_query('''INSERT INTO matches(format, date, tournament_id, match_phase)
                             VALUES(?,?,?,?)''',
                                (tournament.match_format, tournament.start_date, tournament.id,
                                 tournament.scheme_format if tournament.scheme_format else 'League'))
        player1, player2 = players[index]  # eg. 'Player1', 'Player4'
        player1_id, player2_id = get_participants_ids(players[index])
        insert_query('''INSERT INTO matches_has_players_profiles(matches_id, player_profile_id, score)
                        VALUES(?,?,?)''', (match_id, player1_id, 0))
        insert_query('''INSERT INTO matches_has_players_profiles(matches_id, player_profile_id, score)
                        VALUES(?,?,?)''', (match_id, player2_id, 0))
        this_match = MatchTournResponseMod(id=match_id,
                                           player_1=player1,
                                           player_2=player2,
                                           date=tournament.start_date)
        matches.append(this_match)
    return matches


def get_participants_ids(participants: list[str]) -> list[int]:
    players_ids = []
    for player in participants:
        data = read_query('''SELECT id FROM players_profiles
                        WHERE full_name = ?''', (player,))
        players_ids.append(data[0][0])
    return players_ids


def change_match_score(pl_1_id, pl_2_id, match: Match, match_score: SetMatchScoreMod) -> (
        Response | WinnerResponseMode | str):
    pl_1_score = match_score.pl_1_score
    pl_2_score = match_score.pl_2_score

    tournament = tournaments_service.get_tournament_by_id(match.tourn_id)
    if not tournament:
        raise BadRequest(detail='Invalid tournament ID')

    match_format, value = separate_match_format(match)

    if is_match_finished(match.id):
        raise BadRequest(detail='The match has already been finished')

    match_status = match_score.match_finished

    player1_current_score, player2_current_score = get_players_current_score(match.id, pl_1_id, pl_2_id)
    player1_last_result = calculate_final_result(player1_current_score, pl_1_score, value)
    player2_last_result = calculate_final_result(player2_current_score, pl_2_score, value)

    if not isinstance(match.date, datetime):
        raise BadRequest(detail="Set match start date first")
    if datetime.now() < match.date:
        raise BadRequest(detail="Match score cannot be changed before the match has been started")

    if match_format.lower() == 'score limited' and (player1_last_result >= value or player2_last_result >= value):
        result = update_winner_info(tournament.tour_format, tournament, match.id, pl_1_id, player1_last_result,
                                    pl_2_id, player2_last_result)

        player_service.updating_player_opponents(pl_1_id)
        player_service.updating_player_opponents(pl_2_id)
        winner_id = player_service.get_match_winner(match.id)
        if len(winner_id) == 1:
            match_winner = user_service.get_player_profile_by_id(winner_id[0][0])
            return result if result else Response(status_code=200, content=f'Match finished - Score limit reached: {value},'
                                                                       f' player with more points win :'
                                                                       f'{match_winner.full_name}')
        else:
            return result if result else Response(status_code=200,
                                                      content=f'Match finished draw- Score limit reached: {value}')
    elif match_format.lower() == 'time limited' and time_limit_validator(match.date, value):
        result = update_winner_info(tournament.tour_format, tournament, match.id, pl_1_id, player1_last_result,
                                    pl_2_id, player2_last_result)
        player_service.updating_player_opponents(pl_1_id)
        player_service.updating_player_opponents(pl_2_id)
        winner_id = player_service.get_match_winner(match.id)
        if len(winner_id) == 1:
            match_winner = user_service.get_player_profile_by_id(winner_id[0][0])
            return result if result else Response(status_code=200,
                                                  content=f'Match finished - Time limit reached: {value},'
                                                          f' player with more points win :'
                                                          f'{match_winner.full_name}')
        else:
            return result if result else Response(status_code=200,
                                                  content=f'Match finished draw- Time limit reached: {value}')

    if not match_status:
        update_player_score(match.id, pl_1_id, pl_1_score)
        update_player_score(match.id, pl_2_id, pl_2_score)
        player1, player2 = (user_service.get_player_profile_by_id(pl_1_id),
                            user_service.get_player_profile_by_id(pl_2_id))
        return (f'Score updated: {player1.full_name}: {player1_current_score} -> {player1_last_result}, '
                f'{player2.full_name}: {player2_current_score} -> {player2_last_result}')
    elif match_status:
        result = update_winner_info(tournament.tour_format, tournament, match.id, pl_1_id,
                                    player1_last_result, pl_2_id, player2_last_result)
        player_service.updating_player_opponents(pl_1_id)
        player_service.updating_player_opponents(pl_2_id)
        winner_id = player_service.get_match_winner(match.id)
        if len(winner_id) == 1:
            match_winner = user_service.get_player_profile_by_id(winner_id[0][0])
            return result if result else Response(status_code=200,
                                                  content=f'Match finished, winner is {match_winner.full_name}')
        else:
            return result if result else Response(status_code=200,
                                                  content=f'Match finished draw')


def update_winner_info(play_format: str, tournament: Tournament, match_id: int, player1_id: int,
                       player1_score: int, player2_id: int, player2_score: int) -> None | WinnerResponseMode | Response:

    is_final = check_if_match_final(match_id)

    if play_format.capitalize() == 'Knockout':
        if player1_score > player2_score:
            update_query('''UPDATE matches_has_players_profiles
                              SET score = ?, win = 1
                            WHERE matches_id = ? and player_profile_id = ?''', (player1_score, match_id, player1_id))
            update_query('''UPDATE matches_has_players_profiles
                            SET score = ?
                            WHERE matches_id = ? and player_profile_id = ?''', (player2_score, match_id, player2_id))
            player_service.update_player_stat_matches(player1_id, True)
            player_service.update_player_stat_matches(player2_id, False)

            if is_final:
                player_service.update_player_stat_tourn(player2_id, True)
                return create_winner_response(player1_id, tournament.id)
            last_phase = tournaments_service.check_if_knockout_phase_is_over(tournament)
            if last_phase:
                tournaments_service.move_phase(tournament.id, last_phase[1])

        elif player2_score > player1_score:
            update_query('''UPDATE matches_has_players_profiles
                                       SET score = ?, win = 1
                                      WHERE matches_id = ? and player_profile_id = ?''',
                         (player2_score, match_id, player2_id))
            update_query('''UPDATE matches_has_players_profiles
                                        SET score = ?
                                        WHERE matches_id = ? and player_profile_id = ?''',
                         (player1_score, match_id, player1_id))
            player_service.update_player_stat_matches(player2_id, True)
            player_service.update_player_stat_matches(player1_id, False)

            if is_final:
                player_service.update_player_stat_tourn(player2_id, True)
                return create_winner_response(player2_id, tournament.id)
            last_phase = tournaments_service.check_if_knockout_phase_is_over(tournament)
            if last_phase:
                tournaments_service.move_phase(tournament.id, last_phase[-1])

        elif player2_score == player1_score:
            # update_player_score(match_id, player2_id, player2_score)
            # update_player_score(match_id, player1_id, player1_score)
            # когато мачът не е равен и при последното въвеждане на разултат става равен и 
            # се посочи край на мача, събира сегашните точки в базата + подадените точки и скора става Марс.
            raise BadRequest(detail='Knockout matches cannot end draw, please try again.')
    elif play_format.capitalize() == 'League':
        if player1_score > player2_score:
            update_query('''UPDATE matches_has_players_profiles
                                  SET score = ?, win = 1, pts = 2
                                WHERE matches_id = ? and player_profile_id = ?''',
                         (player1_score, match_id, player1_id))
            update_query('''UPDATE matches_has_players_profiles
                                SET score = ?
                                WHERE matches_id = ? and player_profile_id = ?''',
                         (player2_score, match_id, player2_id))
            player_service.update_player_stat_matches(player1_id, True)
            player_service.update_player_stat_matches(player2_id, False)
            winner = tournaments_service.check_if_league_is_over(tournament.id)

            if winner:
                player_service.update_player_stat_tourn(winner, True)
                return create_winner_response(winner, tournament.id)

        elif player2_score > player1_score:
            update_query('''UPDATE matches_has_players_profiles
                                           SET score = ?, win = 1, pts = 2
                                          WHERE matches_id = ? and player_profile_id = ?''',
                         (player2_score, match_id, player2_id))
            update_query('''UPDATE matches_has_players_profiles
                                            SET score = ?
                                            WHERE matches_id = ? and player_profile_id = ?''',
                         (player1_score, match_id, player1_id))
            player_service.update_player_stat_matches(player2_id, True)
            player_service.update_player_stat_matches(player1_id, False)
            winner = tournaments_service.check_if_league_is_over(tournament.id)
            if winner:
                player_service.update_player_stat_tourn(winner, True)
                return create_winner_response(winner, tournament.id)

        elif player2_score == player1_score:
            update_query('''UPDATE matches_has_players_profiles
                                                           SET score = ?, win = 0, pts = 1
                                                          WHERE matches_id = ? and player_profile_id = ?''',
                         (player1_score, match_id, player1_id))
            update_query('''UPDATE matches_has_players_profiles
                                                           SET score = ?, win = 0, pts = 1
                                                          WHERE matches_id = ? and player_profile_id = ?''',
                         (player2_score, match_id, player2_id))
            player_service.upd_player_stat_match_when_draw(player1_id, player2_id)


def get_players_current_score(match_id: int, player1_id: int, player2_id: int) -> tuple[int, int]:
    result = read_query('''SELECT
                                (SELECT score FROM matches_has_players_profiles
                                 WHERE matches_id = ? AND player_profile_id = ?) as player1_score,
                                (SELECT score FROM matches_has_players_profiles
                                 WHERE matches_id = ? AND player_profile_id = ?) as player2_score''',
                        (match_id, player1_id, match_id, player2_id))
    return result[0][0], result[0][1]


def update_player_score(match_id: int, player_id: int, score: int) -> None:
    update_query('''UPDATE matches_has_players_profiles
                    SET score = score + ?
                    WHERE matches_id = ? and player_profile_id = ?''', (score, match_id, player_id))


def create_winner_response(player_id: int, tournament_id: int) -> WinnerResponseMode:
    player = user_service.get_player_profile_by_id(player_id)
    name, country, club = list(get_player_name_club_country(player_id)[0])
    tournament = tournaments_service.get_tournament_by_id(tournament_id)
    tournaments_service.insert_tournament_winner(tournament, player)
    return WinnerResponseMode(champion_name=name, club=club, country=country, tournament_won=tournament.title)


def get_matches_for_tournament(tournament_id: int) -> list[Match]:
    data = read_query('''SELECT * FROM matches WHERE tournament_id = ?''', (tournament_id,))
    result = [Match.from_query_result(*row) for row in data]
    return result


def get_matches_by_tournament_v2(tournament_id: int) -> list[MatchesResponseMod]:
    data = read_query('''SELECT mp.matches_id, pp.full_name, mp.score, m.date, t.title 
                            FROM matches_has_players_profiles mp
                            JOIN matches m ON m.id = mp.matches_id
                            JOIN players_profiles pp ON pp.id = mp.player_profile_id
                            JOIN tournaments t ON m.tournament_id = t.id
                            WHERE t.id = ?''', (tournament_id,))
    return packaging_for_all_matches(data)


def match_exists(match_id: int) -> bool:
    return any(
        read_query(
            '''SELECT 1 FROM matches WHERE id = ?''',
            (match_id,)))


def check_match_finished(match_id: int) -> bool:
    return any(
        read_query(
            '''SELECT 1 FROM matches_has_players_profiles 
	WHERE matches_id = ? and win = 1''', (match_id,)))


def get_matches_ids(tourn_id: int, match_fase: str) -> list[int]:
    match_ids = read_query('''SELECT id FROM matches 
                      WHERE tournament_id = ? and match_phase = ?''',
                           (tourn_id, match_fase.lower()))

    return sorted(match_ids)


def get_winners_ids(match_ids: list[int]) -> list[int]:
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
    update_query(
        "UPDATE tournaments_has_players_profiles SET player_profile_id = ? WHERE tournament_id = ? AND "
        "player_profile_id = ?",
        (new_player.id, tournament.id, old_player.id))
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
                 WHERE id = ?''', (m_date, match_id))

    if not ans:
        raise BadRequest(f'Match date is already set to {m_date}')

    return Response(status_code=200, content=f'Match #{match_id} date set to: {m_date}')


def paginating_matches(page: int,
                       page_size: int | None = 2,
                       sort: str | None = None,
                       sort_by: str | None = None):
    if page <= 0:
        return BadRequest('Page must be equal to or higher than 1.')
    page = (int(page) - 1) * int(page_size)

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
    '''Argument example for ONE match :
    [
        (match_id, full_name, score, date, title),
        (match_id, full_name, score, date, title)
    ]'''

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


def calculate_final_result(player_current_score, pl_last_score, value):
    player_total_score = player_current_score + pl_last_score
    if player_total_score > value:
        return value
    return player_total_score


def is_match_finished(match_id: int) -> bool:
    result = read_query('SELECT COUNT(*) as winner_count FROM matches_has_players_profiles '
                        'WHERE matches_id = ? AND (win = 1 OR win = 0)', (match_id,))
    return result[0][0] > 0


def separate_match_format(match: Match):
    # 'Time Limited: 60 minutes'  -> 'Time Limited', 60
    value = [char for char in match.format if char.isdigit()]
    if not value:
        raise BadRequest('Something went wrong')
    slice_index = match.format.find(':')
    match_format = match.format[:slice_index].strip()
    if not match_format:
        raise BadRequest('Something went wrong')
    value = int(''.join(value))
    return match_format, value


def get_all_finished_league_matches(tournament_id: int) -> list[Match]:
    result = read_query('''SELECT DISTINCT matches_id FROM matches_has_players_profiles AS m 
    INNER JOIN matches AS ma ON m.matches_id = ma.id WHERE m.win IS NOT NULL AND ma.tournament_id = ?''',
                        (tournament_id,))
    matches = [get_match_by_id_v2(*row) for row in result]
    return matches


def get_league_winner(tournament_id: int) -> int | Response | None:
    # Here we get winner upon PTS
    result = read_query('''SELECT player_profile_id, SUM(pts) FROM matches_has_players_profiles 
    INNER JOIN matches AS m ON matches_has_players_profiles.matches_id = m.id WHERE m.tournament_id = ? 
    GROUP BY player_profile_id ORDER BY SUM(pts) DESC LIMIT 2''', (tournament_id,))
    # in case that there are two people with same score
    if result:
        score_p1, score_p2 = result[0][1], result[1][1]
        if score_p1 == score_p2:
            return Response(status_code=200, content='Both players have same score, director has to '
                                                     'choose which player is the winner')
        player_id = result[0][0]
        return player_id
    return None


def get_match_players(match_id):
    player1, player2 = read_query('''SELECT player_profile_id FROM matches_has_players_profiles 
    WHERE matches_id = ?''', (match_id,))
    return player1[0], player2[0]


def get_all_finished_knockout_matches(tournament_id: int, match_phase: str):
    result = read_query('''SELECT DISTINCT matches_id FROM matches_has_players_profiles AS m 
        INNER JOIN matches AS ma ON m.matches_id = ma.id WHERE m.win IS NOT NULL AND ma.tournament_id = ? AND ma.match_phase LIKE ?''',
                        (tournament_id, match_phase))
    matches = [get_match_by_id_v2(*row) for row in result]
    return matches


def get_matches_with_exact_phase(tournament_id: int, match_phase) -> list[Match]:
    data = read_query('''SELECT * FROM matches WHERE tournament_id = ? and match_phase = ?''',
                      (tournament_id, match_phase))
    result = [Match.from_query_result(*row) for row in data]
    return result
