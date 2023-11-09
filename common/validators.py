from common.exceptions import BadRequest

_TOURNAMENT_FORMATS = ('Knockout', 'League')
_MATCH_FORMATS = ('Time limited', 'Score limited')


def tournament_format_validator(tour_format: str):
    if tour_format not in _TOURNAMENT_FORMATS:
        return BadRequest(f"Invalid format {tour_format}, Option must be 'Knockout' or 'League'")
    return tour_format


def match_format_validator(match_format: str):
    if match_format not in _MATCH_FORMATS:
        return BadRequest(f"Invalid format: {match_format}, Option must be 'Time limited' or 'Score limited'")
    return match_format
