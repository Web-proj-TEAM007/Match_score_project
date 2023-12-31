from data.database import insert_query, read_query, update_query
from common.exceptions import BadRequest
from data.models import RequestsResponseModel
from fastapi import Response
from mailjet_rest import Client
import os
from common.validators import _STATUS

def requests(user_role, unprocessed, user_id):

    query = '''SELECT id, request, user_id, player_profile_id FROM requests '''

    where_clauses = []
    params = []

    
    if user_role.lower() != 'admin':
        raise BadRequest('Access not allowed!')
    
    if unprocessed == True:
        where_clauses.append("approved is NULL")
    
    elif user_id != None :
        where_clauses.append("user_id = ?")
        params.append(user_id)
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    data = read_query(query,params)
    
    return (RequestsResponseModel.from_query_result(*row) for row in data)

def handle(user_id, approved, user_role):

    if user_role.lower() != 'admin':
        raise BadRequest('Access not allowed!')
    
    update_query('''UPDATE users, requests SET users.user_role = ?, requests.approved = ?
                  WHERE users.id = ? AND requests.user_id = ?''',
                    ('Director', _STATUS[approved] ,user_id, user_id))

    
    user_email = read_query('''SELECT email from users where id = ?''', (user_id,))

    send_email_director(user_email[0][0], approved, user_role)
    
    if approved == 1:
        return Response(status_code=200, content="Request approved")
    else:
        return Response(status_code=200, content="Request rejected")



    
   
def link(user_id, player_id, approved, user_role):

    

    if user_role.lower() != 'admin':
        raise BadRequest('Access not allowed!')

    update_query('''UPDATE users, requests SET users.player_profile_id = ?, requests.approved = ?
                  WHERE users.id = ? AND requests.user_id = ?''',
                    (player_id, _STATUS[approved] ,user_id, user_id))
    
    user_email = read_query('''SELECT email from users where id = ?''', (user_id,))

    send_email_player(user_email[0][0], approved, user_role)

    if approved == 1:
        return Response(status_code=200, content="Request approved")
    else:
        return Response(status_code=200, content="Request rejected")




    

def send_email_player(user_email, approval, user_role):

    if user_role.lower() != 'admin':
        raise BadRequest('Access not allowed!')

    answer = {}

    if approval == 1:
        answer = {"TextPart": "Your request has been accepted! Good luck in your matches!",
                    "HTMLPart": "<h3>Your request has been accepted!</h3><br />Good luck in your matches!"} 
    else: 
        answer = {"TextPart": "Your request has been denied! Please contact the support on this issue!",
                    "HTMLPart": "<h3>Your request has been denied!</h3><br />Please contact the support on this issue!"}


    """
	This call sends a message to one recipient.
	"""

    api_key = os.getenv('MAIL_API')
    api_secret = os.getenv('MAIL_API_SECRET')
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
	'Messages': [
					{
							"From": {
									"Email": "velislavangelov19@gmail.com",
									"Name": "Admin"
							},
							"To": [
									{
											"Email": f"{user_email}"
									}
							],
							"Subject": "Your player-profile link request",
							"TextPart": f"{answer['TextPart']}",
							"HTMLPart": f"{answer['HTMLPart']}"
					}
			]
	}
    result = mailjet.send.create(data=data)
    print (result.status_code)
    print (result.json())


def send_email_director(user_email, approval, user_role):

    if user_role.lower() != 'admin':
        raise BadRequest('Access not allowed!')

    answer = {}

    if approval == 1:
        answer = {"TextPart": "Your request has been accepted! You have Director privileges!",
                    "HTMLPart": "<h3>Your request has been accepted!</h3><br />You have Director privileges!"} 
    else: 
        answer = {"TextPart": "Your request has been denied! Please contact the support on this issue!",
                    "HTMLPart": "<h3>Your request has been denied!</h3><br />Please contact the support on this issue!"}


    """
    This call sends a message to one recipient.
    """

    api_key = os.getenv('MAIL_API')
    api_secret = os.getenv('MAIL_API_SECRET')
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
	'Messages': [
					{
							"From": {
									"Email": "velislavangelov19@gmail.com",
									"Name": "Admin"
							},
							"To": [
									{
											"Email": f"{user_email}"
									}
							],
							"Subject": "Your Director promotion request",
							"TextPart": f"{answer['TextPart']}",
							"HTMLPart": f"{answer['HTMLPart']}"
					}
			]
	}
    result = mailjet.send.create(data=data)
    print (result.status_code)
    print (result.json())

def tournament_entry_notification(user_email, user_role):

    if user_role.lower() != 'admin':
        raise BadRequest('Access not allowed!')

    """
    This call sends a message to one recipient.
    """

    api_key = os.getenv('MAIL_API')
    api_secret = os.getenv('MAIL_API_SECRET')
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
	'Messages': [
					{
							"From": {
									"Email": "velislavangelov19@gmail.com",
									"Name": "Admin"
							},
							"To": [
									{
											"Email": f"{user_email}"
									}
							],
							"Subject": "Tournament entry notification",
							"TextPart": "Welcome to the tournament! Good luck!",
							"HTMLPart": "<h3>Welcome to the tournament!</h3><br/> Good luck!"
					}
			]
	}
    result = mailjet.send.create(data=data)
    print (result.status_code)
    print (result.json())

def match_entry_notification(user_email, user_role):

    if user_role.lower() != 'admin':
        raise BadRequest('Access not allowed!')

    """
    This call sends a message to one recipient.
    """

    api_key = os.getenv('MAIL_API')
    api_secret = os.getenv('MAIL_API_SECRET')
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
	'Messages': [
					{
							"From": {
									"Email": "velislavangelov19@gmail.com",
									"Name": "Admin"
							},
							"To": [
									{
											"Email": f"{user_email}"
									}
							],
							"Subject": "Match entry notification",
							"TextPart": "You have been added to a match! Good luck!",
							"HTMLPart": "<h3>You have been added to a match!</h3><br/> Good luck!"
					}
			]
	}
    result = mailjet.send.create(data=data)
    print (result.status_code)
    print (result.json())






    
    

