from fastapi import APIRouter, Query, Depends, Path, Body, Response
from data.models import UpdateParticipantModel, TournamentCreateModel
from common.validators import tournament_format_validator, validate_tournament_start_date
from common.exceptions import NotFound, Unauthorized, BadRequest
from services import tournaments_service, match_service, user_service, player_service
from authentication.jwt_bearer import JWTBearer
from authentication.auth import get_user_from_token
from datetime import date

tournaments_router = APIRouter(prefix='/tournaments')


@tournaments_router.get("/", tags=['Tournaments'])
def get_all_tournaments(title: str = Query(None, description="Get tournament by it's title"),
                        tournament_format: str = Query(None, description="Get tournaments by format")):
    """You can get all upcoming tournaments, optional filter features"""
    tournaments = tournaments_service.get_all_tournaments(title, tournament_format)
    if not tournaments:
        raise NotFound('Tournament not found.')
    # ---------------- Add all matches for the specific tournament -------------------
    # for tournament in tournaments:
    #     tournament.matches = match_service.get_matches_for_tournament(tournament.id)
    #     tournament.participants = tournaments_service.get_tournament_participants(tournament.id)
    #     if tournament.matches:
    #         tournament.match_format = tournament.matches[0].format
    return tournaments

@tournaments_router.get("/league-ranking/{tournament_id}", tags=['Tournaments'])
def get_league_ranking(tournament_id: int):

    tournament = tournaments_service.get_tournament_by_id(tournament_id)

    if not tournament:
        raise NotFound(f'Tournament #{tournament_id} not found.')

    if tournament.tour_format.lower() != 'league':
        raise BadRequest('Currently ranking is available only for League format.')
    
    return tournaments_service.get_ranking_league(tournament_id)

@tournaments_router.post("/", tags=['Tournaments'])
def create_tournament(tournament: TournamentCreateModel, token: str = Depends(JWTBearer())):
    """Only director can create tournaments"""
    user = get_user_from_token(token)
    if user is None or user.user_role.lower() != 'director':
        raise Unauthorized(detail='Only directors can create a tournament')
    if tournaments_service.tournament_exists(tournament.title):
        return Response(f'{tournament.title} already exists')
    players = tournament.participants.copy()
    player_schema = tournaments_service.generate_knockout_schema(players) \
        if tournament_format_validator(tournament.tour_format) == 'knockout' \
        else tournaments_service.generate_league_schema(players)
    players_profiles_ids = [user_service.create_player_statistic(user_service.create_player_profile(name)) for name in
                            tournament.participants if not user_service.player_profile_exists(name)]
    if not players_profiles_ids:
        players_profiles_ids = [user_service.get_player_profile_by_fullname(name).id for name in tournament.participants]
    _ = [player_service.update_player_stat_tourn(pl_id, False) for pl_id in players_profiles_ids]
    tournament = tournaments_service.create_tournament(tournament)
    tournament.scheme_format = "One vs all" if tournament.tour_format.lower() == 'league' else (
        tournaments_service.get_scheme_format(len(tournament.participants)))
    _ = tournaments_service.insert_participants_into_tournament(players_profiles_ids, tournament.id)
    tournament.matches = match_service.create_matches(tournament, player_schema)
    return tournament


@tournaments_router.get("/{id}", tags=['Tournaments'])
def get_tournament_by_id(tournament_id: int = Query(..., description='Enter desired tournament id')):
    tournament = tournaments_service.get_tournament_by_id_v2(tournament_id)
    if not tournament:
        raise NotFound(detail='No such tournament')
    if not tournament.start_date:
        tournament.start_date = 'Not set yet'
    return tournament


@tournaments_router.patch("/date/{tour_id}", tags=['Tournaments'])
def manage_tournament(tour_id: int = Path(..., description='Enter tournament id'),
                      change_tournament_start_date: date = Body(None,
                                                                description='Change tournament start date'),
                      token: str = Depends(JWTBearer())):
    """Only director can change date tournaments"""
    user = get_user_from_token(token)
    if user.user_role.lower() != 'director':
        raise Unauthorized(detail='Only directors can manage a tournament')
    tournament = tournaments_service.get_tournament_by_id(tour_id)
    if not tournament:
        raise NotFound(f'Tournament with id: {tour_id}, does not exist.')
    if change_tournament_start_date:
        if tournament.start_date:
            validate_tournament_start_date(tournament.start_date, change_tournament_start_date)
    result = tournaments_service.manage_tournament(tournament, change_tournament_start_date, None)
    return result


@tournaments_router.patch("/participants/{tour_id}", tags=['Tournaments'])
def manage_participants(tour_id: int = Path(..., description='Enter tournament id'),
                      update_participants: UpdateParticipantModel = Body(None,
                                                                         description='Update participants'),
                      token: str = Depends(JWTBearer())):
    """Only director can manage tournaments"""
    user = get_user_from_token(token)
    if user.user_role.lower() != 'director':
        raise Unauthorized(content='Only directors can manage a tournament')
    tournament = tournaments_service.get_tournament_by_id(tour_id)
    if not tournament:
        raise NotFound(f'Tournament with id: {tour_id}, does not exist.')
    if update_participants:
        tournaments_service.validate_participants(tournament, update_participants)
    result = tournaments_service.manage_tournament(tournament, None, update_participants)
    return result
