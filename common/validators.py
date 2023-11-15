from datetime import datetime
from services import user_service
from common.exceptions import BadRequest, NotFound

_TOURNAMENT_FORMATS = ('Knockout', 'League')
_MATCH_FORMATS = ('Time limited', 'Score limited')
_MATCH_PHASES = ('final', 'semi-final', 'quarterfinals', 'eight-final')

def tournament_format_validator(tour_format: str):
    if tour_format not in _TOURNAMENT_FORMATS:
        raise BadRequest(f"Invalid format {tour_format}, Option must be 'Knockout' or 'League'")
    return tour_format


def match_format_validator(match_format: str):
    if match_format not in _MATCH_FORMATS:
        raise BadRequest(f"Invalid format: {match_format}, Option must be 'Time limited' or 'Score limited'")
    return match_format


def check_date(date: str | datetime):
    if date != datetime:
        return 'not set yet'
    return date


def validate_tournament_start_date(old_date, new_date):
    if new_date <= old_date and new_date <= datetime.now():
        raise ValueError('The tournament start date cannot be in the past')


def validate_participants(tournament, update_participants):
    _ = [user_service.create_player_statistic(user_service.create_player_profile(name)) for name in
         update_participants if not user_service.player_profile_exists(name)]
    if update_participants.new_player in tournament.participants:
        raise BadRequest(f'Player: {update_participants.new_player} is already in the tournament')
    if update_participants.old_player not in tournament.participants:
        raise NotFound(f'Player: {update_participants.old_player} is not part of the tournament participants')
    
def check_score(score: int | None):

    if score is None:
        return 0
    else:
        return score