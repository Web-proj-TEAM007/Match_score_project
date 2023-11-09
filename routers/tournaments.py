from fastapi import APIRouter, Query, Depends, Path
from data.models import Tournament, Match, TournamentCreateModel, Player, UpdateParticipantModel
from common.validators import tournament_format_validator
from common.exceptions import NoContent, NotFound, Unauthorized
from services import tournaments_service, match_serivce, player_service
from authentication.jwt_bearer import JWTBearer
from datetime import datetime

tournaments_router = APIRouter(prefix='/tournaments')


@tournaments_router.get('/')
def get_all_tournaments(title: str = Query(None, description="Get tournament by it's title"),
                        tournament_format: str = Query(None, description="Get tournaments by format")):
    """You can get all upcoming tournaments, optional filter features"""
    tournaments = tournaments_service.get_all_tournaments(title, tournament_format_validator(tournament_format))
    if not tournaments:
        raise NoContent('No available tournaments')
    # ---------------- Add all matches for the specific tournament -------------------
    # result = [matches_service.get_matches_for_tournaments(tour.id) for tour in tournaments]
    # return result


@tournaments_router.post('/')
def create_tournament(tournament: TournamentCreateModel, token: Depends(JWTBearer())):
    """Only director can create tournaments"""
    # ----------- check if user is authorized to create a tournament -------------------
    # user = get_user_from_token(token)
    # if user.user_role != 'Director':
    #   raise Unauthorized(content='Only directors can create a tournament')
    # ---------- check if each player is already existing, if not create one and link it to profile --------
    # players = [player_service.create_player_statistic(player_service.create_player(name)) for name in
    #            tournament.participants if not player_service.exists(name)]
    # ------------------------------- waiting for player implementation -----------------------------------
    # schema = tournaments_service.get_scheme_format(len(players))
    # result = tournaments_service.generate_schema(players)
    if tournament.tour_format == "Knockout":
        #  --------- here we randomly assign every player to a match depending on the schema ----------
        # RETURN OF SCHEMA AND RESULT:
        #   eight-finals
        #   [{'first_player': 'Player5', 'second_player': 'Player3'}, {'first_player': 'Player5','second_player':
        #   'Player3'},{'first_player': 'Player7', 'second_player': 'Player6'},
        #   {'first_player': 'Player7', 'second_player': 'Player6'}]
        # ------------- further implementation of creating these matches ---------
        # knockout_schema = [match_service.create_match(match) for match in result]
        pass
    elif tournament.tour_format == "League":
        pass


@tournaments_router.get("/{tournament-id}")
def get_tournament_by_id(tour_id: int = Path(..., description='Enter desired tournament id')):
    tournament = tournaments_service.get_tournament_by_id(tour_id)
    # here will need to see how the matches are returned so i can make tournament start date by the first match that is
    # going to be played that day
    tournament.matches = match_serivce.get_matches_for_tournament(tournament.id)
    tournament.participant = tournaments_service.get_tournament_participants(tournament.id)
    return tournament


@tournaments_router.patch("/manage-event/{tournament-id}")
def manage_tournament(tour_id: int = Path(..., description='Enter tournament id'),
                      change_tournament_start_date: datetime = Query(None,
                                                                     description='Change tournament start date'),
                      update_participants: UpdateParticipantModel = Query(None,
                                                                          description='Update participants')):
    """Only director can manage tournaments"""
    tournament = tournaments_service.get_tournament_by_id(tour_id)
    if not tournament:
        raise NotFound(f'Tournament with id: {tour_id}, does not exists.')
    if not change_tournament_start_date or update_participants:
        manage_tournament()
    # -- check if the date that want to be changed is not in the past
    if change_tournament_start_date < tournament.start_date and change_tournament_start_date < datetime.now():
        raise ValueError('The tournament start date cannot be in the past')
    if update_participants:
        players = [player_service.create_player_statistic(player_service.create_player(name)) for name in
                   update_participants if not player_service.exists(name)]
    # Have to make further check if the new_player not already in the same tournament, if he is playing in other match(
    # if he does remove the match he was playing and reconfigure the schema
    # assuming we have make the needed validations
    result = tournaments_service.manage_event(tournament, change_tournament_start_date, update_participants)
