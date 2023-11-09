from common.exceptions import Unauthorized
from data.models import User
from services.user_service import email_exists
from authentication.jwt_handler import decode_jwt

def get_user_from_token(token: str) -> User:
    decoded_token = decode_jwt(token)
    email = decoded_token.get("email")
    user = email_exists(email)
    return user
