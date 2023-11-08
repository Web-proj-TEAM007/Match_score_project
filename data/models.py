from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from common.validators import tournament_format_validator, match_format_validator
from datetime import datetime


class Player(BaseModel):
    id: Optional[int]
    full_name: constr(pattern=r'^[a-zA-Z\s\-]+$')
    country: Optional[str]
    sport_club: Optional[str]

    @classmethod
    def from_query_result(cls, id, full_name, country, sport_club):
        return cls(id=id,
                   full_name=full_name,
                   country=country,
                   sport_club=sport_club,
                   )


class RegisterUser(BaseModel):
    id: Optional[int]
    email: EmailStr
    password: str
    players: list[Player]

    @classmethod
    def from_query_result(cls, id, email, password, players):
        return cls(id=id,
                   email=email,
                   password=password,
                   players=players,
                   )


class Match(BaseModel):
    id: Optional[int]
    date: datetime
    match_format: str
    time_limit: Optional[datetime]
    score_limit: Optional[int]

    @classmethod
    def from_query_result(cls, id, date, format, time_limit, score_limit):
        return cls(id=id,
                   date=date,
                   format=match_format_validator(format),
                   time_limit=time_limit,
                   score_limit=score_limit
                   )


class Tournament(BaseModel):
    id: Optional[int]
    title: str
    tour_format: str
    prize: str
    matches: Optional[Match]

    @classmethod
    def from_query_result(cls, id, title, tour_format, prize):
        return cls(id=id,
                   title=title,
                   tour_format=tour_format,
                   prize=prize,
                   )


class TournamentCreateModel(BaseModel):
    title: str
    tour_format: str
    prize: str
    participants: list[Player]


class League(BaseModel):
    # requires scoring for loss, draw and, win
    pass
