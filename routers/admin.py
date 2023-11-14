from fastapi import APIRouter, Depends, Response
from services import admin_service
from authentication.jwt_bearer import JWTBearer
from authentication.auth import get_user_from_token


admin_router = APIRouter(prefix='/admin')

@admin_router.get('/requests')
def get_all(user_id: int = None,  
            token: str = Depends(JWTBearer())):
    
    user = get_user_from_token(token)
    return admin_service.requests(user.user_role,user_id)

@admin_router.put('/requests/director')
def director_promotion(user_id: int = None,  
                    token: str = Depends(JWTBearer())):
    
    '''In order to promote a user you must get their id'''
    
    user = get_user_from_token(token)

    return admin_service.handle(user_id, user.user_role)

@admin_router.put('/requests/player')
def link_profile(user_id: int = None, 
                 player_id: int = None,
                 token: str = Depends(JWTBearer())):
    
    user = get_user_from_token(token)

    return admin_service.link(user_id, player_id, user.user_role)


    



