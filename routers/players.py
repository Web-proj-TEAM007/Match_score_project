from fastapi import APIRouter, Depends, Response
from common.exceptions import NotFound
from services import player_service, user_service
from authentication.jwt_bearer import JWTBearer
from data.models import Input_player

players_router = APIRouter(prefix='/players')


@players_router.get("/{player_id}", tags=['Player'])
def get_player_byID(player_id: int):

    if not player_service.player_exists_id(player_id):
        raise NotFound(f'Player #{player_id} not found.')

    return player_service.get_player_by_id(player_id)    

@players_router.post('/profile', tags=['Player'])
def create_profile(data: Input_player, token: str = Depends(JWTBearer())):
    """Create profile with you name and country. Sport club is optional."""

    player = player_service.create_player_profile(data.full_name, data.country, data.sport_club)
    user_service.create_player_statistic(player)
    return Response(status_code=200, content="Profile created successfully")
