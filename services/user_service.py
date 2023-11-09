import bcrypt
from authentication.jwt_handler import sign_jwt
from data.database import insert_query, read_query, update_query
from common.exceptions import BadRequest
from data.models import User


def create_user(email: str, password: str):
    # validation for the email
    if email_exists(email):
        return BadRequest(content=f'User with {email} is already registered')
    # bcrypt is being used for the purposes of hashing the password / 'utf-8' is the algorithm, gensalt() is
    # generating random 'salt'(bytes) which are added to the hashed password for secure purposes
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    insert_query("INSERT INTO users(email, password, user_role) VALUES(?,?,?)",
                 (email, hashed_password, 'user'))
    return sign_jwt(email)


def log_in(email: str, password: str):
    # We are taking the user's hashed password from the DB
    stored_password_hashes = read_query('''SELECT password FROM users
                           WHERE email = ?''', (email,))
    # Check if there is a returned value
    if not stored_password_hashes:
        return BadRequest(f'Invalid login.')
    # Extract the first password hash from the result
    stored_password_hash = stored_password_hashes[0][0]
    # Convert the provided password to bytes
    password_bytes = password.encode('utf-8')
    # Check if the provided password matches the stored password hash
    if bcrypt.checkpw(password_bytes, stored_password_hash.encode('utf-8')):
        data = read_query('''SELECT id, email, password, user_role FROM users
                               WHERE email = ?''', (email,))
        user = next((User.from_query_result(*row) for row in data), None)
        # Return user access token or BadRequest
        return sign_jwt(user.email)
    else:
        return BadRequest(f'Invalid login.')
    

def profile(fullname: str, country: str, club: str = None):

    insert_query('''INSERT INTO players_profiles(full_name, country, club) VALUES(?,?,?)''',
                    (fullname, country, club))

def email_exists(email: str | None = None) -> bool:
    if email:
        return any(read_query("SELECT 1 FROM users WHERE email = ?", (email,)))



    





