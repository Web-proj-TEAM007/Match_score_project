from fastapi import APIRouter, Query, Depends, Path, Body, Response
from data.models import UpdateParticipantModel, NewPhase, TournamentCreateModel
from common.validators import (tournament_format_validator, validate_tournament_start_date, validate_participants,
                               _MATCH_PHASES)
from common.exceptions import NoContent, NotFound, Unauthorized, BadRequest
from services import tournaments_service, match_service, user_service
from authentication.jwt_bearer import JWTBearer
from authentication.auth import get_user_from_token
from datetime import date

tournaments_router = APIRouter(prefix='/tournaments')


@tournaments_router.get("/")
def get_all_tournaments(title: str = Query(None, description="Get tournament by it's title"),
                        tournament_format: str = Query(None, description="Get tournaments by format")):
    """You can get all upcoming tournaments, optional filter features"""
    tournaments = tournaments_service.get_all_tournaments(title, tournament_format)
    if not tournaments:
        return Response(status_code=204, headers={'detail': 'No available tournaments'})
    # ---------------- Add all matches for the specific tournament -------------------
    for tournament in tournaments:
        tournament.matches = match_service.get_matches_for_tournament(tournament.id)
        tournament.participants = tournaments_service.get_tournament_participants(tournament.id)
    return tournaments


@tournaments_router.post("/")
def create_tournament(tournament: TournamentCreateModel, token: str = Depends(JWTBearer())):
    """Only director can create tournaments"""
    # ----------- check if user is authorized to create a tournament -------------------
    user = get_user_from_token(token)
    if user.user_role != 'Director':
        raise Unauthorized(detail='Only directors can create a tournament')
    # ----------- check if tournament already exists ---------------------------
    if tournaments_service.tournament_exists(tournament.title):
        return Response(f'{tournament.title} already exists')
    # ---------- check if each player is already existing, if not, create one and link it to profile --------
    players = tournament.participants.copy()
    player_profiles_id = [user_service.create_player_statistic(user_service.create_player_profile(name)) for name in
                          players if not user_service.player_profile_exists(name)]
    tournament = tournaments_service.create_tournament(tournament)
    _ = tournaments_service.insert_participants_into_tournament(player_profiles_id, tournament.id)
    if tournament_format_validator(tournament.tour_format) == "Knockout":
        player_schema = tournaments_service.generate_knockout_schema(players)
        tournament.scheme_format = tournaments_service.get_scheme_format(len(tournament.participants))
    elif tournament_format_validator(tournament.tour_format) == "League":
        tournament.scheme_format = "League"
        player_schema = tournaments_service.generate_league_schema(players)
    tournament.matches = match_service.create_matches(tournament, player_schema)
    return tournament


@tournaments_router.get("/{id}")
def get_tournament_by_id(tournament_id: int = Query(..., description='Enter desired tournament id')):
    tournament = tournaments_service.get_tournament_by_id(tournament_id)
    if not tournament:
        raise NotFound(detail='No such tournament')
    tournament.matches = match_service.get_matches_for_tournament(tournament.id)
    tournament.start_date = tournaments_service.get_tournament_start_date(tournament)
    if not tournament.start_date:
        tournament.start_date = 'Not set yet'
    return tournament


@tournaments_router.patch("/manage-event/{tour_id}")
def manage_tournament(tour_id: int = Path(..., description='Enter tournament id'),
                      change_tournament_start_date: date = Query(None,
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
        if tournament.start_date:
            validate_tournament_start_date(tournament.start_date, change_tournament_start_date)
    if update_participants:
        validate_participants(tournament, update_participants)
    result = tournaments_service.manage_tournament(tournament, change_tournament_start_date, update_participants)
    return result


@tournaments_router.put("/{tournament_id}/phases")
def move_phase(tournament_id: int, current_phase: NewPhase, token: str = Depends(JWTBearer())):
    user = get_user_from_token(token)
    if user.user_role != 'Director':
        raise Unauthorized(content='Only directors can change tournament phase')
    tournament_exists = tournaments_service.tournament_exists_by_id(tournament_id)
    if not tournament_exists:
        raise NotFound(f'Tournament #{tournament_id} not found.')

    if current_phase.current_phase not in _MATCH_PHASES:
        raise BadRequest('Invalid phase.')

    match_ids = match_service.get_matches_ids(tournament_id, current_phase.current_phase)
    winners_reversed = match_service.get_winners_ids(match_ids)

    return match_service.create_next_phase(winners_reversed, current_phase.current_phase, tournament_id)
