from data.database import read_query, update_query, insert_query
from data.models import PlayerStatistics
from common.validators import check_date
from services import user_service, tournaments_service
from common.validators import check_date, check_score, _MATCH_PHASES, _SORT_BY_VAL
from datetime import datetime, date
from common.exceptions import BadRequest
from fastapi import Response


def get_player_by_id(pl_id: int):

    data = read_query('''SELECT pp.id, pp.full_name, pp.country, pp.club, 
                                    ps.matches_played, ps.matches_won, ps.tournaments_played, ps.tournaments_won, ps.ratio 
                        FROM players_statistics ps
                            JOIN players_profiles pp ON pp.id = ps.player_profile_id
                            WHERE pp.id = ?''', (pl_id,))
    
    return next((PlayerStatistics.from_query_result(*row) for row in data), None)

def player_exists_id(pl_id: int) -> bool:

    return any(
        read_query('''SELECT 1 FROM players_statistics
                   WHERE player_profile_id = ?''', (pl_id,)))

def update_player_stat_matches(player_id: int, win: bool) -> None | BadRequest:
    # ratio = win / loss - според изискванията. Какво да връщам и да въвеждам в базата, ако играчът няма победи? За сега формулата по-долу.
    # ratio = win / matches_played - Показва коеф. на успеяваемост, струва ми се по-логично...

    if win:
        ans =update_query('''UPDATE players_statistics SET matches_won = matches_won + 1, 
                                                            matches_played = matches_played + 1, 
                                                            ratio = matches_won / matches_played
                            WHERE player_profile_id = ?''', (player_id,))
    else:
        ans =update_query('''UPDATE players_statistics SET matches_played = matches_played + 1, 
                                                            ratio = matches_won / matches_played
                            WHERE player_profile_id = ?''', (player_id,))


    if not ans:
        raise BadRequest('Updating player match stats went wrong.')

def update_player_stat_tourn(player_id: int, t_win: bool) -> None | BadRequest:

    if t_win:
        ans = update_query('''UPDATE players_statistics 
                                SET tournaments_won = tournaments_won + 1, 
                                    tournaments_played = tournaments_played + 1
                            WHERE player_profile_id = ?''', (player_id,))
    else:
        ans = update_query('''UPDATE players_statistics 
                                SET tournaments_played = tournaments_played + 1
                            WHERE player_profile_id = ?''', (player_id,))
    
    if not ans:
        raise BadRequest('Updating player tournament stats went wrong.')