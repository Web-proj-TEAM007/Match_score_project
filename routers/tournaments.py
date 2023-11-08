from fastapi import APIRouter, Query, Depends, Path
from data.models import Tournament, Match, TournamentCreateModel, Player
from common.validators import tournament_format_validator
from common.exceptions import NoContent, NotFound
from services import tournaments_service
from authentication.jwt_bearer import JWTBearer

tournaments_router = APIRouter(prefix='/tournaments')


@tournaments_router.get('/')
def get_all_tournaments(title: str = Query(None, description="Get tournament by it's title"),
                        tournament_format: str = Query(None, description="Get tournaments by format")):
    """You can get all upcoming tournaments, optional filter features"""
    tournaments = tournaments_service.get_all_tournaments(title, tournament_format_validator(tournament_format))
    if not tournaments:
        raise NoContent('No available tournaments')
    # Add all matches for the specific tournament
    # for tournament in tournaments:
    #     tournament.matches = matches_service.get_matches_for_tournaments(tournament.id)
    return tournaments


@tournaments_router.post('/')
def create_tournament(tournament: TournamentCreateModel, token: Depends(JWTBearer())):
    """Only director can create tournaments"""
    if tournament.tour_format == "Knockout":
        # ---------- check if each player is already existing, if not create one and link it to profile --------
        # ------------------------------- waiting for player implementation ------------------------------------
        # players = []
        # for player_name in tournament.participants:
        #     if not player_service.exists(player_name):
        #         player = player_service.create_player(player_name)
        #         player_service.create_profile_for_player(player)
        #         players.append(player)
        # schema = tournaments_service.get_scheme_format(len(players))
        #  --------- here we randomly assign every player to a match depending on the schema ----------
        # result = tournaments_service.generate_knockout_scheme(players)
        # RETURN OF SCHEMA AND RESULT:
        #   eight-finals
        #   [{'first_player': 'Player5', 'second_player': 'Player3'}, {'first_player': 'Player5','second_player':
        #   'Player3'},{'first_player': 'Player7', 'second_player': 'Player6'},
        #   {'first_player': 'Player7', 'second_player': 'Player6'}]
        # ------------- further implementation of creating these matches ---------
        pass
    elif tournament.tour_format == "League":
        pass
