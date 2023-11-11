from fastapi import APIRouter, Query, Depends, Path
from datetime import datetime
from services import tournaments_service, match_service
from common.exceptions import NoContent, NotFound, BadRequest
from authentication.jwt_bearer import JWTBearer
# from authentication.auth import get_user_from_token
from data.models import Match, Tournament

match_router = APIRouter(prefix='/matches')


@match_router.get("/")
def get_all_matches(sort_by_date: datetime = Query(None, description='Filter by day in a following format '
                                                                     'YYYY-MM-DDTHH:MM:SS eg. 2023-10-21T00:00:00 :'),
                    sort_by_tournament_id: int = Query(default=None, description='Search by topic id')):
    """You can get all existing matches, optional filter features"""
    # matches = match_service.get_all_matches(sort_by_date, sort_by_tournament_id)
    # if not matches:
    #     raise NotFound(content='No matches')
    # return matches


@match_router.get('/{match_id}')
def get_match_by_id(match_id: int):

    ans = match_service.match_exists(match_id)
    if not ans:
        return NotFound(f'Match #{match_id} not found.')

    return match_service.get_match_by_id(match_id)

# @match_serivce.post("/")
# def create_match(create_match: Match, token: str = Depends(JWTBearer())):
#     """Enter the needed requirements for the match to be created"""
#     # user = get_user_from_token(token)
#     # if user.is_director:
#     match = match_serivce.create_match(create_match)
#     return match
