from fastapi import APIRouter, Depends, Response
from services import admin_service, user_service
from authentication.jwt_bearer import JWTBearer
from authentication.auth import get_user_from_token
from data.models import Link_profile, Player_Director_ApproveMailer, Notify_player, Director_promotion
from fastapi.responses import JSONResponse
from common.exceptions import BadRequest, NotFound
from common.validators import validate_user_roles


admin_router = APIRouter(prefix='/admin')


@admin_router.get('/requests', tags=['Admin'])
def get_all(user_id: int = None,
            unprocessed: bool = False,
            token: str = Depends(JWTBearer())):
    """See all requests"""

    user = get_user_from_token(token)
    return admin_service.requests(user.user_role, unprocessed, user_id)


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
    if not user_service.user_exists(data.user_id):
        raise BadRequest(f'User with id: {data.user_id} not found')
    if not user_service.get_player_profile_by_id(data.player_id):
        raise BadRequest(f'User with id: {data.player_id} not found')
    if user_service.is_user_linked_to_a_profile(user):
        linked_profile = user_service.get_user_player_profile_full_name(user)
        raise BadRequest(f'Already linked to a profile with full name: {linked_profile}')
    return admin_service.link(data.user_id, data.player_id, data.approved, user.user_role)



# @admin_router.post('/send_notification_player', tags=['Admin'])
# def send_notification_player(data: Player_Director_ApproveMailer, token: str = Depends(JWTBearer())):
#     '''Send notification to player that his request is accepted or denied'''
#     user = get_user_from_token(token)
#     admin_service.send_email_player(data.email, data.approval, user.user_role)
#     return JSONResponse(status_code=200, content={'message': "Notification sent!"})



# @admin_router.post('/send_notification_director', tags=['Admin'])
# def send_notification_director(data: Player_Director_ApproveMailer, token: str = Depends(JWTBearer())):
#     '''Send notification to a user that his request is accepted or denied'''
#     user = get_user_from_token(token)
#     admin_service.send_email_director(data.email, data.approval, user.user_role)
#     return JSONResponse(status_code=200, content={'message': "Notification sent!"})




# @admin_router.post('/tournament-join-alert', tags=['Admin'])
# def tournament_join_alert(data: Notify_player, token: str = Depends(JWTBearer())):
#     '''Send notification to a player that he is added to a tournament'''
#     user = get_user_from_token(token)
#     admin_service.tournament_entry_notification(data.email, user.user_role)
#     return JSONResponse(status_code=200, content={'message': "Notification sent!"})



# @admin_router.post('/player-added-alert', tags=['Admin'])
# def player_added_alert(data: Notify_player, token: str = Depends(JWTBearer())):
#     '''Send notification to a player that he is added to a match'''
#     user = get_user_from_token(token)
#     admin_service.match_entry_notification(data.email, user.user_role)
#     return JSONResponse(status_code=200, content={'message': "Notification sent!"})


@admin_router.put('/{user_id}', tags=['Admin'])
def change_user_role(user_id: int, new_role: str, token: str = Depends(JWTBearer())):
    """Change a user role"""
    user = get_user_from_token(token)
    if user.user_role != 'admin':
        raise BadRequest('Access not allowed!')
    if user.user_role == new_role:
        raise BadRequest(f'User role is already: {user.user_role}')
    ans = user_service.user_exists(user_id)
    if not ans:
        raise NotFound(f'User #{user_id} not found.')
    user_role = validate_user_roles(new_role)
    # shte e hubavo da shlqpnem da hodi request kum bazata
    return user_service.change_user_role(user_id, user_role)