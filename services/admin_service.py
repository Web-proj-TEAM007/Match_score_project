from data.database import insert_query, read_query, update_query
from common.exceptions import BadRequest
from data.models import RequestsResponseModel
from fastapi import Response

def requests(user_role, user_id):
    
    if user_role != 'admin':
        return BadRequest('Access not allowed!')
    
    if user_id == None:
        data = read_query('''SELECT id, request, user_id FROM requests ''')
    else:
        data = read_query('''SELECT id, request, user_id FROM requests 
                                WHERE user_id = ?''',(user_id,))
    
    return (RequestsResponseModel.from_query_result(*row) for row in data)

def handle(user_id,user_role):

    if user_role != 'admin':
        return BadRequest('Access not allowed!')
    
    update_query('''UPDATE users SET user_role = ? WHERE id = ?''',
                    ('Director', user_id,))
    update_query('''DELETE FROM requests WHERE user_id = ? ''',(user_id,))
    
    return Response(status_code=200)
   
def link(user_id,player_id,user_role):

    if user_role != 'admin':
        return BadRequest('Access not allowed!')

    update_query('''UPDATE users SET player_profile_id = ? WHERE id = ?''',
                    (player_id, user_id,))
    update_query('''DELETE FROM requests WHERE user_id = ? ''',(user_id,))

    return Response(status_code=201, content="Request accepted")
    

    





    
    

