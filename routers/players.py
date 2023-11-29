from fastapi import APIRouter, Depends, Response
from common.exceptions import NoContent, NotFound, BadRequest, Unauthorized
from services import player_service



players_router = APIRouter(prefix='/players')


@players_router.get("/{player_id}", tags=['Player'])
def get_player_byID(player_id: int):

    if not player_service.player_exists_id(player_id):
        raise NotFound(f'Player #{player_id} not found.')

    return player_service.get_player_by_id(player_id)    
