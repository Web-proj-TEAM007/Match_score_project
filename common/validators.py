from datetime import datetime

from common.exceptions import BadRequest

_TOURNAMENT_FORMATS = ('Knockout', 'League')
_MATCH_FORMATS = ('Time limited', 'Score limited')
_MATCH_FASES = ('final', 'semi-final', 'quarterfinals', 'eight-final')


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

def check_score(score: int | None):

    if score is None:
        return 0
    else:
        return score
