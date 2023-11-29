from fastapi import APIRouter, Depends, Response
from services import user_service
from authentication.jwt_bearer import JWTBearer
from data.models import RegisterUser, LoginData, Input_player, Request_Link_profile
from authentication.auth import get_user_from_token
from common.exceptions import NotFound


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


@users_router.post('/profile', tags=['User'])
def create_profile(data: Input_player, token: str = Depends(JWTBearer())):
    """Create profile with you name and country. Sport club is optional."""

    user_service.create_player_profile(data.full_name, data.country, data.sport_club)
    return Response(status_code=200, content="Profile created successfully")

@users_router.post('/promote', tags=['User'])
def promote_to_director(token: str = Depends(JWTBearer())):
    """Request to be promoted to director"""
    user = get_user_from_token(token)
    return user_service.promotion(user.id)



@users_router.post('/requests/', tags=['User'])
def make_request(profile: Request_Link_profile, token: str = Depends(JWTBearer())):
    """Request to link your player profile with your user registration."""
    user = get_user_from_token(token)
    return user_service.request(user.id, profile.player_id)


@users_router.put('/{user_id}', tags=['User'])
def change_user_role(user_id: int, new_role: str):
    """Change a user role upon request"""

    ans = user_service.user_exists(user_id)
    if not ans:
        raise NotFound(f'User #{user_id} not found.')

    return user_service.change_user_role(user_id, new_role)
