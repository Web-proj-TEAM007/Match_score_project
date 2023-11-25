from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from common.validators import tournament_format_validator, match_format_validator, check_date
from datetime import datetime
from datetime import date


class Player(BaseModel):
    id: Optional[int] = None
    full_name: constr(pattern=r'^[a-zA-Z\s\-]+$')
    country: Optional[str] = None
    sport_club: Optional[str] = None

    @classmethod
    def from_query_result(cls, id, full_name, country, sport_club):
        return cls(id=id,
                   full_name=full_name,
                   country=country,
                   sport_club=sport_club,
                   )


class RegisterUser(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    password: str

    @classmethod
    def from_query_result(cls, id, email, password):
        return cls(id=id,
                   email=email,
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
    def from_query_result(cls, id, email, password, user_role, ):
        return cls(id=id,
                   email=email,
                   password=password,
                   user_role=user_role,
                   )


class Match(BaseModel):
    id: int | None = None
    format: str
    date: datetime | str = 'not set yet'
    tourn_id: int
    match_phase: str

    @classmethod
    def from_query_result(cls, id, format, date, tourn_id, match_phase):
        return cls(
            id=id,
            format=format,
            date=check_date(date),
            tourn_id=tourn_id,
            match_phase=match_phase)


class MatchTournResponseMod(BaseModel):
    id: int
    player_1: str
    player_2: str
    date: datetime | str


class MatchResponseMod(BaseModel):
    id: int
    tournament_title: str
    player_1: str
    player_2: str
    date: datetime | str
    match_fase: str


class SetMatchScoreMod(BaseModel):
    tourn_id: int
    pl_1_id: int
    pl_1_score: int
    pl_2_id: int
    pl_2_score: int
    match_finished: bool


class TournamentBase(BaseModel):
    title: str
    tour_format: str
    prize: int
    match_format: Optional[str] | None = None
    participants: list[str] | None = None


class Tournament(TournamentBase):
    id: Optional[int] = None
    scheme_format: str | None = None
    matches: Optional[Match] | None = None
    start_date: Optional[date] = None
    winner: str | None = None

    @classmethod
    def from_query_result(cls, id, title, tour_format, prize, start_date, winner):
        return cls(id=id,
                   title=title,
                   tour_format=tour_format,
                   prize=prize,
                   start_date=start_date,
                   winner=winner
                   )


class TournamentCreateModel(TournamentBase):
    start_date: date


class League(BaseModel):
    # requires scoring for loss, draw and, win
    pass


class UpdateParticipantModel(BaseModel):
    old_player: str
    new_player: str


class RequestsResponseModel(BaseModel):
    id: int
    request: str
    user_id: int

    @classmethod
    def from_query_result(cls, id, request, user_id):
        return cls(id=id,
                   request=request,
                   user_id=user_id)


class NewPhase(BaseModel):
    current_phase: str


class Link_profile(BaseModel):
    user_id: int
    player_id: int


class Request_Link_profile(BaseModel):
    player_id: int

class WinnerResponseMode(BaseModel):
    champion_name: str
    club: str | None
    country: str | None
    tournament_won: str

class MatchesResponseMod(BaseModel):
    match_id: int
    score: str
    match_date: datetime | None
    tournament_title: str

class SetMatchDate(BaseModel):
    date: datetime


class PlayerStatistics(Player):
    matches_played: int
    tournaments_played: int
    tournaments_won: int
    wl_ratio: str
    most_played_against: str | None
    best_opponent: str | None
    worst_opponent: str | None

    @classmethod
    def from_query_result(cls, id, full_name, country, 
                          sport_club, matches_played, 
                          tournaments_played, tournaments_won, wl_ratio, 
                          most_played_against, best_opponent, worst_opponent):
        return cls(id=id,
                   full_name=full_name,
                   country=country,
                   sport_club=sport_club,
                   matches_played=matches_played,
                   tournaments_played=tournaments_played,
                   tournaments_won=tournaments_won,
                   wl_ratio=wl_ratio,
                   most_played_against=most_played_against,
                   best_opponent=best_opponent,
                   worst_opponent=worst_opponent)

class Player_Director_ApproveMailer(BaseModel):
    email: str
    approval: int

class Notify_player(BaseModel):
    email: str