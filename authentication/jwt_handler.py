import time
import jwt
import os
from dotenv import load_dotenv
from common.exceptions import BadRequest

load_dotenv()

_JWT_SECRET = os.getenv('SECRET')
_JWT_ALGORITHM = os.getenv('ALGORITHM')


# This function return generated token
def token_response(token: str):
    return {"access-token": token}


# Create a JWT token
def sign_jwt( user_email: str):
    payload = {
        "user_email": user_email,
        "date_created": time.time(),
        "exp_date": time.time() + 60000000}
    token = jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)
    return token_response(token)


# Decode a JWT token
def decode_jwt(token: str):
    try:
        decoded_token = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
    except:
        return None

    if decoded_token['exp_date'] >= time.time():
        return decoded_token
    else:
        raise BadRequest('Please log-in again')
