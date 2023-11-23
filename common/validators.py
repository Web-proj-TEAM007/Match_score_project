from datetime import datetime, timedelta
from services import user_service
from common.exceptions import BadRequest, NotFound

_TOURNAMENT_FORMATS = ('Knockout', 'League')
_MATCH_FORMATS = ('Time limited', 'Score limited')
_MATCH_PHASES = ('final', 'semi-final', 'quarterfinals', 'eight-final')
_SORT_BY_VAL = ('date', 'tournament_id')


def tournament_format_validator(tour_format: str):
    if tour_format not in _TOURNAMENT_FORMATS:
        raise BadRequest(f"Invalid format {tour_format}, Option must be 'Knockout' or 'League'")
    return tour_format


def match_format_validator(match_format: str):
    if match_format not in _MATCH_FORMATS:
        raise BadRequest(f"Invalid format: {match_format}, Option must be 'Time limited' or 'Score limited'")
    return match_format


def check_date(date: str | datetime):
    if not isinstance(date, datetime):
        return 'not set yet'
    return date


def validate_tournament_start_date(old_date, new_date):
    if new_date <= old_date and new_date <= datetime.now():
        raise ValueError('The tournament start date cannot be in the past')


def validate_participants(tournament, update_participants):
    if update_participants.new_player in tournament.participants:
        raise BadRequest(f'Player: {update_participants.new_player} is already in the tournament')
    if not any(player.full_name == update_participants.old_player for player in tournament.participants):
        raise NotFound(f'Player: {update_participants.old_player} is not part of the tournament participants')
    _ = user_service.create_player_statistic(user_service.create_player_profile(update_participants.new_player))


def check_score(score: int | None):

    if score is None:
        return 0
    else:
        return score


def time_limit_validator(match_date, limit):
    # match_date = 2023-11-30 10:00:00 , limit = 60 (minutes)
    time_limit = match_date + timedelta(minutes=limit)
    return time_limit < datetime.now()
