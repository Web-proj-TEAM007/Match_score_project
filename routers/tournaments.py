from fastapi import APIRouter, Query, Depends, Path, Body, Response
from data.models import Tournament, Match, Player, UpdateParticipantModel
from common.validators import tournament_format_validator, validate_tournament_start_date, validate_participants
from common.exceptions import NoContent, NotFound, Unauthorized, BadRequest
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
    # ----------- check if tournament already exists ---------------------------
    if tournaments_service.tournament_exists(tournament.title):
        return Response(f'{tournament.title} already exists')
    # ---------- check if each player is already existing, if not create one and link it to profile --------
    _ = [user_service.create_player_statistic(user_service.create_player_profile(name)) for name in
         tournament.participants if not user_service.player_profile_exists(name)]
    # ---- make a variable players which get participants, when inserted in generate_game_schema the func empty it.--
    players = tournament.participants.copy()
    # ----- get the format which is for e.g. 'semi-final' etc. (Which will be good to go to match service and change it
    # everytime the matches change) --------
    tournament.scheme_format = tournaments_service.get_scheme_format(len(tournament.participants))
    # ----- this return dict of all player which are randomly separated by couples
    generated_players_schema = tournaments_service.generate_game_schema(players)
    if tournament.tour_format == "Knockout":
        tournament.tour_format = "Knockout"
    elif tournament.tour_format == "League":
        tournament.tour_format = "League"
    # ---- creating tournament in the db -------
    tournament = tournaments_service.create_tournament(tournament)
    # match_schema = match_service.create_match(tournament)
    # ----- create a list of all matches in the tournament ----
    match_schema = match_service.create_match_v2(tournament, generated_players_schema)
    # assign them to the object attribute and return it
    tournament.matches = match_schema
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
        raise NotFound(f'Tournament with id: {tour_id}, does not exist.')
    if change_tournament_start_date:
        validate_tournament_start_date(tournament.start_date, change_tournament_start_date)
    if update_participants:
        validate_participants(tournament, update_participants)
    result = tournaments_service.manage_tournament(tournament, change_tournament_start_date, update_participants)
    return result

