from data.database import read_query, update_query, insert_query
from data.models import PlayerStatistics
from common.validators import form_ratio
from common.exceptions import BadRequest


def get_player_by_id(pl_id: int):

    data = read_query('''SELECT pp.id, pp.full_name, pp.country, pp.club, ps.matches_won, ps.matches_lost,
                                    ps.matches_played, ps.tournaments_played, ps.tournaments_won, 
                                    ps.most_played_opp, ps.best_opp, ps.worst_opp
                        FROM players_statistics ps
                            JOIN players_profiles pp ON pp.id = ps.player_profile_id
                            WHERE pp.id = ?''', (pl_id,))
    
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


def update_player_stat_tourn(player_id: int, t_win: bool) -> None | BadRequest:

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

def updating_player_opponents(player_id: int) -> None | BadRequest: 
    
    ans = update_query('''UPDATE players_statistics 
                    SET best_opp = (WITH matchess as
                                    (SELECT matches_id FROM matches_has_players_profiles
                                    WHERE player_profile_id = ?)
                            SELECT pp.full_name 
                            FROM matches_has_players_profiles mp, matchess ms, players_statistics ps, players_profiles pp
                            WHERE mp.player_profile_id != ? and ms.matches_id = mp.matches_id 
                                AND ps.player_profile_id = mp.player_profile_id and pp.id = mp.player_profile_id
                            GROUP BY mp.player_profile_id
                            ORDER BY (ps.matches_won/ps.matches_played) desc, pp.full_name
                            LIMIT 1),
                    worst_opp = (WITH matchesss as
                                    (SELECT matches_id FROM matches_has_players_profiles
                                    WHERE player_profile_id = ?)
                            SELECT pp.full_name 
                            FROM matches_has_players_profiles mp, matchesss ms, players_statistics ps, players_profiles pp
                            WHERE mp.player_profile_id != ? and ms.matches_id = mp.matches_id 
                                AND ps.player_profile_id = mp.player_profile_id and pp.id = mp.player_profile_id
                            GROUP BY mp.player_profile_id
                            ORDER BY (ps.matches_won/ps.matches_played) asc, pp.full_name
                            LIMIT 1),
                    most_played_opp = (WITH matchessss AS
                                                (SELECT matches_id FROM matches_has_players_profiles
                                                WHERE player_profile_id = ?)
                            SELECT full_name FROM matches_has_players_profiles mp
                            JOIN players_profiles pp ON pp.id = mp.player_profile_id
                            JOIN matchessss m ON m.matches_id = mp.matches_id and mp.player_profile_id != ?
                            GROUP BY player_profile_id
                            ORDER BY COUNT(mp.player_profile_id) desc, full_name desc
                            LIMIT 1)
                    WHERE player_profile_id = ?''', (player_id, player_id, player_id, player_id, player_id, player_id, player_id))

    if not ans:
        raise BadRequest('Updating player opponents went wrong.')
