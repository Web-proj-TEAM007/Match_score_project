from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from common.validators import tournament_format_validator, match_format_validator, check_date
from datetime import datetime


class Player(BaseModel):
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
    email: EmailStr
    password: str
    
    @classmethod
    def from_query_result(cls, email, password):
        return cls(email=email,
                   password=password,
                   )
    
class LoginData(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: str
    password: str
    user_role: str
    


    @classmethod
    def from_query_result(cls, id, email, password, user_role,):
        return cls(id=id,
                   email=email,
                   password=password,
                   user_role=user_role,
                   )
    



class Match(BaseModel):
    id: int | None = None
    format: str
    date: datetime
    tourn_id: int

    @classmethod
    def from_query_result(cls, id, format, date, tourn_id):
        return cls(
            id=id,
            format=format,
            date=check_date(date),
            tourn_id=tourn_id)


class Tournament(BaseModel):
    id: Optional[int]
    title: str
    tour_format: str
    prize: int
    matches: Optional[Match]
    participant: list[str]
    start_date: Optional[datetime]

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
    prize: int
    participants: list[str]


class League(BaseModel):
    # requires scoring for loss, draw and, win
    pass


class UpdateParticipantModel(BaseModel):
    old_player: str
    new_player: str
