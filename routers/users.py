from fastapi import APIRouter, Depends, Response
from services import user_service, player_service
from authentication.jwt_bearer import JWTBearer
from data.models import RegisterUser, LoginData, Input_player, Request_Link_profile
from authentication.auth import get_user_from_token
from common.exceptions import NotFound, BadRequest



users_router = APIRouter(prefix='/users')


@users_router.post('/register', tags=['User'])
def register_user(data: RegisterUser):
    """Register with email and password"""
    user = user_service.create_user(data.email, data.password)
    return user


@users_router.post('/log-in', tags=['User'])
def user_login(data: LoginData):
    """Login with email and password"""
    user = user_service.log_in(data.email, data.password)
    return user


@users_router.post('/promote', tags=['User'])
def promote_to_director(token: str = Depends(JWTBearer())):
    """Request to be promoted to director"""
    user = get_user_from_token(token)
    return user_service.promotion(user.id)



@users_router.post('/requests/', tags=['User'])
def make_request(profile: Request_Link_profile, token: str = Depends(JWTBearer())):
    """Request to link your player profile with your user registration."""
    user = get_user_from_token(token)
    if not user_service.get_player_profile_by_id(profile.player_id):
        raise BadRequest(f'Player with id: {profile.player_id} do not exist')
    if user_service.is_user_linked_to_a_profile(user):
        linked_profile = user_service.get_user_player_profile_full_name(user)
        raise BadRequest(f'Already linked to a profile with full name: {linked_profile}')
    return user_service.request(user.id, profile.player_id)


