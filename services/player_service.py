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