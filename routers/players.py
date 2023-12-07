from fastapi import APIRouter, Depends, Response
from common.exceptions import NotFound, Unauthorized
from services import player_service, user_service
from authentication.jwt_bearer import JWTBearer
from data.models import Input_player, PlayerEdit
from authentication.auth import get_user_from_token

players_router = APIRouter(prefix='/players')


@players_router.get("/{player_id}", tags=['Player'])
def get_player_byID(player_id: int):

    if not player_service.player_exists_id(player_id):
        raise NotFound(f'Player #{player_id} not found.')

    return player_service.get_player_by_id(player_id)   

@players_router.put('/{player_id}/edit', tags=['Player'])
def edit_player(player_id: int, edited_player: PlayerEdit, 
                token: str = Depends(JWTBearer())):
    'Edit player by providing all the requested information in the body.'

    user = get_user_from_token(token)

    if not player_service.player_exists_id(player_id):
        raise NotFound(f'Player #{player_id} not found.')
    
    linked = player_service.check_player_linked(player_id)
    user_is_player = player_service.user_is_player(user.id, player_id)
    
    if user.user_role.lower() == 'director' and not linked:
        player_service.edit_player(player_id, edited_player)
        return Response(status_code=200, content='Player updated.')
    elif linked and user_is_player:
        player_service.edit_player(player_id, edited_player)
        return Response(status_code=200, content='Player updated.')
    
    raise Unauthorized('Request denied.') 

@players_router.post('/profile', tags=['Player'])
def create_profile(data: Input_player, token: str = Depends(JWTBearer())):
    """Create profile with you name and country. Sport club is optional."""

    user = get_user_from_token(token)

    if user.user_role.lower() != 'director':
        raise Unauthorized(f'Request denied, only Directors can create player profile.')

    player = player_service.create_player_profile(data.full_name, data.country, data.sport_club)
    user_service.create_player_statistic(player)
    return Response(status_code=200, content="Profile created successfully")
