from fastapi import APIRouter, Depends, Response
from services import admin_service
from authentication.jwt_bearer import JWTBearer
from authentication.auth import get_user_from_token
from data.models import Link_profile, Player_Director_ApproveMailer, Notify_player, Director_promotion
from fastapi.responses import JSONResponse


admin_router = APIRouter(prefix='/admin')


@admin_router.get('/requests', tags=['Admin'])
def get_all(user_id: int = None,
            token: str = Depends(JWTBearer())):
    """See all requests"""

    user = get_user_from_token(token)
    return admin_service.requests(user.user_role, user_id)


@admin_router.put('/requests/director', tags=['Admin'])
def director_promotion(data: Director_promotion,
                       token: str = Depends(JWTBearer())):
    '''In order to promote a user to director you must put their id'''

    user = get_user_from_token(token)
    return admin_service.handle(data.user_id, data.approved, user.user_role)



@admin_router.put('/requests/player', tags=['Admin'])
def link_profile(data: Link_profile,
                 token: str = Depends(JWTBearer())):
    '''In order to link a user with a player profile you must put their id and the player profile id'''

    user = get_user_from_token(token)
    return admin_service.link(data.user_id, data.player_id, data.approved ,user.user_role)



@admin_router.post('/send_notification_player', tags=['Admin'])
def send_notification_player(data: Player_Director_ApproveMailer, token: str = Depends(JWTBearer())):
    '''Send notification to player that his request is accepted or denied'''
    user = get_user_from_token(token)
    admin_service.send_email_player(data.email, data.approval, user.user_role)
    return JSONResponse(status_code=200, content={'message': "Notification sent!"})



@admin_router.post('/send_notification_director', tags=['Admin'])
def send_notification_director(data: Player_Director_ApproveMailer, token: str = Depends(JWTBearer())):
    '''Send notification to a user that his request is accepted or denied'''
    user = get_user_from_token(token)
    admin_service.send_email_director(data.email, data.approval, user.user_role)
    return JSONResponse(status_code=200, content={'message': "Notification sent!"})




@admin_router.post('/tournament-join-alert', tags=['Admin'])
def tournament_join_alert(data: Notify_player, token: str = Depends(JWTBearer())):
    '''Send notification to a player that he is added to a tournament'''
    user = get_user_from_token(token)
    admin_service.tournament_entry_notification(data.email, user.user_role)
    return JSONResponse(status_code=200, content={'message': "Notification sent!"})



@admin_router.post('/player-added-alert', tags=['Admin'])
def player_added_alert(data: Notify_player, token: str = Depends(JWTBearer())):
    '''Send notification to a player that he is added to a match'''
    user = get_user_from_token(token)
    admin_service.match_entry_notification(data.email, user.user_role)
    return JSONResponse(status_code=200, content={'message': "Notification sent!"})
