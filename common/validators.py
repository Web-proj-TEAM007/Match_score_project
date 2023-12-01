from datetime import datetime, timedelta, date
from common.exceptions import BadRequest, NotFound


_TOURNAMENT_FORMATS = ('knockout', 'league')
_MATCH_FORMATS = ('time limited', 'score limited')
_MATCH_PHASES = ('final', 'semi-final', 'quarterfinals', 'eight-final')
_SORT_BY_VAL = ('date', 'tournament_id')
_STATUS = (False, True)
_USER_ROLES = ('admin', 'director', 'user')


def tournament_format_validator(tour_format: str):
    if tour_format.lower() not in _TOURNAMENT_FORMATS:
        raise BadRequest(f"Invalid format {tour_format}, Option must be 'knockout' or 'league'")
    return tour_format.lower()


def match_format_validator(match_format: str):
    if match_format.lower() not in _MATCH_FORMATS:
        raise BadRequest(f"Invalid format: {match_format}, Option must be 'Time limited' or 'Score limited'")
    return match_format.lower()


def check_date(date: str | datetime):
    if not isinstance(date, datetime):
        return 'not set yet'
    return date


def validate_tournament_start_date(old_date, new_date):
    date_now = datetime.now().date()
    if new_date == old_date:
        raise BadRequest(detail=f'Tournament start date is already set to {new_date}')
    if new_date < old_date or new_date <= date_now:
        raise BadRequest(detail='The tournament start date cannot be in the past')


def check_score(score: int | None):

    if score is None:
        return 0
    else:
        return score


def time_limit_validator(match_date, limit):
    # match_date = 2023-11-30 10:00:00 , limit = 60 (minutes)
    time_limit = match_date + timedelta(minutes=limit)
    return time_limit < datetime.now()

def form_ratio(matches_won: int, matches_lost: int) -> str:
    #should return '3/6'

    ratio = str(matches_won) + '/' + str(matches_lost)
    return ratio


def validate_user_roles(user_role: str):
    if user_role.lower() not in _USER_ROLES:
        raise BadRequest(f'{user_role} not a valid user role')
    return user_role.lower()


def validate_match_date(match, new_date: date):
    # match_date = match.date.date()
    if not isinstance(match.date, datetime):
        return new_date
    elif match.date.date() < new_date:
        return new_date
    else:
        return match.date
