from fastapi import HTTPException


class BadRequest(HTTPException):
    def __init__(self, detail=''):
        super().__init__(status_code=400, detail=detail)


class NotFound(HTTPException):
    def __init__(self, detail=''):
        super().__init__(status_code=404, detail=detail)


class Unauthorized(HTTPException):
    def __init__(self, detail=''):
        super().__init__(status_code=403, detail=detail)


class NoContent(HTTPException):
    def __init__(self):
        super().__init__(status_code=204)


class InternalServerError(HTTPException):
    def __init__(self):
        super().__init__(status_code=500)
