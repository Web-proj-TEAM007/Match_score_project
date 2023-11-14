from fastapi import APIRouter, Depends, Response
from services import user_service
from authentication.jwt_bearer import JWTBearer
from data.models import RegisterUser, LoginData, Player
from authentication.auth import get_user_from_token
from common.exceptions import NotFound


users_router = APIRouter(prefix='/users')


@users_router.post('/register')
def register_user(data: RegisterUser):
    user = user_service.create_user(data.email,data.password)
    return user

@users_router.post('/log-in')
def user_login(data: LoginData):
    user = user_service.log_in(data.email,data.password)
    return user


@users_router.post('/profile')
def create_profile(data: Player, token: str = Depends(JWTBearer())):

    user = get_user_from_token(token)

    user_service.create_player_profile(data.full_name, user.id, data.country, data.sport_club)

    return Response("Profile created successfuly")


@users_router.post('/promote')
def promote_to_director(token: str = Depends(JWTBearer())):
    user = get_user_from_token(token)

    return user_service.promotion(user.id)

@users_router.post('/user/request')
def make_request(token: str = Depends(JWTBearer())):
    pass


@users_router.put('/{user_id}')
def change_user_role(user_id: int, new_role: str):

    ans = user_service.user_exists(user_id)
    if not ans:
        raise NotFound(f'User #{user_id} not found.')
    
    return user_service.change_user_role(user_id, new_role)