from data.database import read_query, update_query, insert_query
from data.models import PlayerStatistics, Player, PlayerEdit, User
from common.validators import form_ratio
from common.exceptions import BadRequest


def get_player_by_id(pl_id: int):

    data = read_query('''SELECT pp.id, pp.full_name, pp.country, pp.club, ps.matches_won, ps.matches_lost,
                                    ps.matches_played, ps.tournaments_played, ps.tournaments_won, 
                                    ps.most_played_opp, ps.best_opp, ps.worst_opp
                        FROM players_statistics ps
                            JOIN players_profiles pp ON pp.id = ps.player_profile_id
                            WHERE pp.id = ?''', (pl_id,))
    
    if data:
        ratio = form_ratio(data[0][4], data[0][5])
        data[0] = list(data[0])
        data[0].pop(4)
        data[0].pop(4)

    return next((PlayerStatistics.from_query_result(id=id,full_name=full_name,country=country,sport_club=sport_club,
                                                    matches_played=matches_played,
                                                    tournaments_played=tournaments_played,
                                                    tournaments_won=tournaments_won,wl_ratio=ratio,
                                                    most_played_against=most_played_opp, 
                                                    best_opponent=best_opp, worst_opponent=worst_opp) 
                                                    for id,full_name,country,sport_club,
                                                            matches_played,tournaments_played,tournaments_won,
                                                            most_played_opp,best_opp,worst_opp in data), None)

def player_exists_id(pl_id: int) -> bool:

    return any(
        read_query('''SELECT 1 FROM players_statistics
                   WHERE player_profile_id = ?''', (pl_id,)))

def update_player_stat_matches(player_id: int, win: bool) -> None | BadRequest:

    if win:
        ans = update_query('''UPDATE players_statistics SET matches_won = matches_won + 1, 
                                                            matches_played = matches_played + 1 
                            WHERE player_profile_id = ?''', (player_id,))
    else:
        ans = update_query('''UPDATE players_statistics SET matches_played = matches_played + 1, 
                                                            matches_lost = matches_lost + 1
                            WHERE player_profile_id = ?''', (player_id,))

    if not ans:
        raise BadRequest('Updating player match stats went wrong.')


def upd_player_stat_match_when_draw(player_1_id: int, player_2_id: int) -> BadRequest | None:
    ans_player_1 = update_query('''UPDATE players_statistics 
                                 SET matches_played = matches_played + 1
                                 WHERE player_profile_id = ?''', (player_1_id,))

    ans_player_2 = update_query('''UPDATE players_statistics 
                                 SET matches_played = matches_played + 1
                                 WHERE player_profile_id = ?''', (player_2_id,))

    if not ans_player_1 or not ans_player_2:
        raise BadRequest(f'Updating draw match with players #{player_1_id} and #{player_2_id} went wrong.')

def update_player_stat_tourn(player_id: int, t_win: bool) -> None | BadRequest:

    if not check_if_player_has_stats(player_id):
        creat_pl_stat(player_id)

    if t_win:
        ans = update_query('''UPDATE players_statistics 
                            SET tournaments_won = tournaments_won + 1 
                            WHERE player_profile_id = ?''', (player_id,))
    else:
        ans = update_query('''UPDATE players_statistics 
                            SET tournaments_played = tournaments_played + 1
                            WHERE player_profile_id = ?''', (player_id,))

    if not ans:
        raise BadRequest('Updating player tournament stats went wrong.')

def updating_player_opponents(player_id: int) -> None: 
    
    upd_most_played_opp(player_id)
    upd_best_played_opp(player_id)
    upd_worst_played_opp(player_id)


def get_match_winner(match_id: int) -> list[int] | None:
    result = read_query('SELECT player_profile_id FROM matches_has_players_profiles WHERE matches_id = ? '
                        'AND (win = 1 OR win = 0)', (match_id,))
    return result if result else None


def create_player_profile(full_name: str, country: str | None = None,  sport_club: str | None = None):
    generated_id = insert_query('''INSERT INTO players_profiles(full_name, country, club) VALUES(?,?,?)''',
                                (full_name, country, sport_club))
    player = Player(full_name=full_name, country=country, sport_club=sport_club)
    player.id = generated_id
    return player

def edit_player(player_id: int, new_player: PlayerEdit) -> None:

    update_query('''UPDATE players_profiles 
                    SET full_name = ?, country = ?, club = ?
                    WHERE id = ? ''',
                        (new_player.new_name, new_player.new_country, 
                         new_player.new_club, player_id))

def check_player_linked(player_id: int) -> bool:

    return any(
        read_query('''SELECT 1 FROM users
                   WHERE player_profile_id = ? ''', (player_id,)))

def user_is_player(user_id: int, player_id: int):

    return any(
        read_query('''SELECT 1 FROM users
                   WHERE id = ? and player_profile_id = ?''',
                   (user_id, player_id)))

def check_if_player_has_stats(player_id: int) -> bool:

    return any(
        read_query('''SELECT 1 FROM players_statistics
                   WHERE player_profile_id = ?''', (player_id,)))

def creat_pl_stat(player_id: int) -> None:

    insert_query("INSERT INTO players_statistics(player_profile_id) VALUES(?)", (player_id,))

def upd_most_played_opp(player_id: int) -> None:

    update_query(''' UPDATE players_statistics
                    SET most_played_opp = (WITH matchessss AS
                                                (SELECT matches_id FROM matches_has_players_profiles
                                                WHERE player_profile_id = ?)
                            SELECT full_name FROM matches_has_players_profiles mp
                            JOIN players_profiles pp ON pp.id = mp.player_profile_id
                            JOIN matchessss m ON m.matches_id = mp.matches_id and mp.player_profile_id != ?
                            GROUP BY player_profile_id
                            ORDER BY COUNT(mp.player_profile_id) desc, full_name desc
                            LIMIT 1)
                    WHERE player_profile_id = ?''', (player_id, player_id, player_id))

def upd_best_played_opp(player_id: int) -> None:

    update_query('''UPDATE players_statistics
                 SET best_opp = (WITH matchess as
                                    (SELECT matches_id FROM matches_has_players_profiles
                                    WHERE player_profile_id = ?)
                            SELECT pp.full_name 
                            FROM matches_has_players_profiles mp, matchess ms, players_statistics ps, players_profiles pp
                            WHERE mp.player_profile_id != ? and ms.matches_id = mp.matches_id 
                                AND ps.player_profile_id = mp.player_profile_id and pp.id = mp.player_profile_id
                            GROUP BY mp.player_profile_id
                            ORDER BY (CASE WHEN ps.matches_played > 0 THEN (ps.matches_won/ps.matches_played) ELSE 0 
                            END) desc, pp.full_name
                            LIMIT 1)
                 WHERE player_profile_id = ?''', (player_id, player_id, player_id))

def upd_worst_played_opp(player_id: int) -> None:

    update_query('''UPDATE players_statistics 
                 SET worst_opp = (WITH matchesss as
                                    (SELECT matches_id FROM matches_has_players_profiles
                                    WHERE player_profile_id = ?)
                            SELECT pp.full_name 
                            FROM matches_has_players_profiles mp, matchesss ms, players_statistics ps, players_profiles pp
                            WHERE mp.player_profile_id != ? and ms.matches_id = mp.matches_id 
                                AND ps.player_profile_id = mp.player_profile_id and pp.id = mp.player_profile_id
                            GROUP BY mp.player_profile_id
                            ORDER BY (CASE WHEN ps.matches_played > 0 THEN (ps.matches_won/ps.matches_played) ELSE 0 
                            END) asc, pp.full_name
                            LIMIT 1)
                 WHERE player_profile_id = ?''', (player_id, player_id, player_id))