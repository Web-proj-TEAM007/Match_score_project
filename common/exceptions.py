from fastapi import HTTPException


class BadRequest(HTTPException):
    def __init__(self, content=''):
        super().__init__(status_code=400, content=content)


class NotFound(HTTPException):
    def __init__(self, content=''):
        super().__init__(status_code=404, content=content)


class Unauthorized(HTTPException):
    def __init__(self, content=''):
        super().__init__(status_code=403, content=content)


class NoContent(HTTPException):
    def __init__(self):
        super().__init__(status_code=204)


class InternalServerError(HTTPException):
    def __init__(self):
        super().__init__(status_code=500)
