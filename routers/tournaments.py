from fastapi import APIRouter, Query, Depends, Path, Body, Response
from data.models import Tournament, Match, Player, UpdateParticipantModel
from common.validators import tournament_format_validator
from common.exceptions import NoContent, NotFound, Unauthorized
from services import tournaments_service, match_service, user_service
from authentication.jwt_bearer import JWTBearer
from authentication.auth import get_user_from_token
from datetime import datetime

tournaments_router = APIRouter(prefix='/tournaments')


@tournaments_router.get("/")
def get_all_tournaments(title: str = Query(None, description="Get tournament by it's title"),
                        tournament_format: str = Query(None, description="Get tournaments by format")):
    """You can get all upcoming tournaments, optional filter features"""
    tournaments = tournaments_service.get_all_tournaments(title, tournament_format)
    if not tournaments:
        return Response(status_code=204, headers={'detail': 'No available tournaments'})
    # ---------------- Add all matches for the specific tournament -------------------
    for tour in tournaments:
        tour.matches = match_service.get_matches_for_tournament(tour.id)
    return tournaments


@tournaments_router.post("/")
def create_tournament(tournament: Tournament):
    # token: str = Depends(JWTBearer())): ----- Waiting for request implementation
    """Only director can create tournaments"""
    # ----------- check if user is authorized to create a tournament -------------------
    # user = get_user_from_token(token)
    # if user.user_role != 'Director':     --------- Waiting for request implementation
    #     raise Unauthorized(detail='Only directors can create a tournament')
    # ---------- check if each player is already existing, if not create one and link it to profile --------
    if tournaments_service.tournament_exists(tournament.title):
        # to make more adequate response
        return Response(f'{tournament.title} already exists')
    result = [user_service.create_player_statistic(user_service.create_player_profile(name)) for name in
              tournament.participants if not user_service.player_profile_exists(name)]
    players = tournament.participants.copy()
    schema_t = tournaments_service.get_scheme_format(len(tournament.participants))
    result = tournaments_service.generate_game_schema(tournament.participants) # Шахин: тука губиш participants, защото директно подаваш оригиналния лист и премахваш играчите във функцията.
    if tournament.tour_format == "Knockout":
        tournament.participants = players # Шахин: тука ги връщам обратно. Може да подаваш директно players или друг лист .copy() за да правиш промени в него, а не в оригиналния лист.
        created_tournament = tournaments_service.create_tournament(tournament) 
        knockout_match_schema = match_service.create_match(created_tournament) # Шахин: не итерирай тука, аз го правя във функцията, късно се усетих...
        created_tournament.matches = knockout_match_schema
        created_tournament.scheme = schema_t
        created_tournament.match_format = tournament.match_format
        created_tournament.participants = players
        return created_tournament
    elif tournament.tour_format == "League":
        pass
    return tournament


@tournaments_router.get("/{id}")
def get_tournament_by_id(tournament_id: int = Query(..., description='Enter desired tournament id')):
    tournament = tournaments_service.get_tournament_by_id(tournament_id)
    if not tournament:
        raise NotFound(detail='No such tournament')
    tournament.matches = match_service.get_matches_for_tournament(tournament.id)
    tournament.participants = tournaments_service.get_tournament_participants(tournament.id)
    return tournament
    # here will need to see how the matches are returned so i can make tournament start date by the first match that is
    # going to be played that day


@tournaments_router.patch("/manage-event/{tournament-id}")
def manage_tournament(tour_id: int = Path(..., description='Enter tournament id'),
                      change_tournament_start_date: datetime = Query(None,
                                                                     description='Change tournament start date'),
                      update_participants: UpdateParticipantModel = Body(None,
                                                                         description='Update participants'),
                      token: str = Depends(JWTBearer())):
    """Only director can manage tournaments"""
    user = get_user_from_token(token)
    if user.user_role != 'Director':
        raise Unauthorized(content='Only directors can manage a tournament')
    tournament = tournaments_service.get_tournament_by_id(tour_id)
    if not tournament:
        raise NotFound(f'Tournament with id: {tour_id}, does not exists.')
    if not change_tournament_start_date or update_participants:
        manage_tournament()
    # -- check if the date that want to be changed is not in the past
    if change_tournament_start_date < tournament.start_date and change_tournament_start_date < datetime.now():
        raise ValueError('The tournament start date cannot be in the past')
    if update_participants:
        old, new = [user_service.create_player_statistic(user_service.create_player_profile(name)) for name in
                    update_participants if not user_service.player_profile_exists(name)]
    # Have to make further check if the new_player not already in the same tournament, if he is playing in other match(
    # if he does remove the match he was playing and reconfigure the schema
    # assuming we have make the needed validations
    result = tournaments_service.manage_event(tournament, change_tournament_start_date, update_participants)
