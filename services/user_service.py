import bcrypt
from authentication.jwt_handler import sign_jwt
from data.database import insert_query, read_query, update_query
from common.exceptions import BadRequest
from data.models import User, Player
from typing import Optional
from fastapi import Response


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


def create_player_profile(full_name: str, user_id: int, country: Optional[str] = None,  sport_club: Optional[str] = None):
    generated_id = insert_query('''INSERT INTO players_profiles(full_name, country, club) VALUES(?,?,?)''',
                                (full_name, country, sport_club))
    player = Player(full_name=full_name, country=country, sport_club=sport_club)
    player.id = generated_id

    insert_query('''INSERT INTO requests(request, user_id, player_profile_id) VALUES(?,?,?) ''',
                        ("player profile", user_id, generated_id))

    return player



def email_exists(email: str | None = None) -> User:
    
        
    data = read_query('''SELECT id, email, password, user_role FROM users 
                            WHERE email = ?''',
                      (email,))
    
    return next((User.from_query_result(*row) for row in data), None)
    


def player_profile_exists(full_name) -> bool:
    return any(read_query("SELECT 1 FROM players_profiles WHERE full_name = ?", (full_name,)))


def create_player_statistic(player: Player):
    data = insert_query("INSERT INTO players_statistics(player_profile_id) VALUES(?)", (player.id,))
    return data


def get_player_profile_by_id(profile_id: int):
    data = read_query("SELECT id, full_name, country, club FROM players_profiles WHERE id = ?", (profile_id,))
    player = next((Player.from_query_result(*row) for row in data), None)
    return player


def promotion(user_id):

    insert_query('''INSERT INTO requests(request, user_id) VALUES(?,?) ''',
                        ("Director",user_id,))
    
    return Response(status_code=200, content='Request sent')

def user_exists(user_id: int) -> bool:

    return any(
        read_query(
            '''SELECT 1 FROM users
            WHERE id = ?''', (user_id,)))

def change_user_role(user_id: int, new_role: str):

    ans = update_query('''UPDATE users SET user_role = ?
                       WHERE id = ?''', (new_role, user_id))
    if ans:
        return Response(status_code=200, content=f'User #{user_id} role updated to {new_role}.')
    else:
        raise BadRequest('Something went wrong.')