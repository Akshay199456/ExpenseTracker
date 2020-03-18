from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('user', __name__, url_prefix = '/user')



def display_buttons(db):
	'''
	Displays the appropriate buttons depending on the kind of friend request
	Currently have three different type of requests:
		1. 'Send Request' -> sends a friend request to the user
		2. 'Request Sent' -> user has already sent a friend request to the appropriate user
							but has not been accepted yet
		3. 'Friend' -> Friend Request has been accepted

	Might also need to add here that if the user who has received the friend request rejects
	the request, the user who sent it should be able to see the 'Send Request' button
	'''
	print('Current user id from display_buttons: ', g.user['id'])

	# Return dictionary user_id of those people to whom friend_request has been sent but has not been accepted
	all_friend_request_sent = db.execute(
		'SELECT * FROM friendrequest'
		' WHERE user_id = ? AND friend_type_request = ?', (g.user['id'], 0)
	).fetchall()

	print('All friend request sent: ', all_friend_request_sent)
	friend_request_sent_set = set()
	for item in all_friend_request_sent:
		friend_request_sent_set.add(item['friend_id'])
	print('Friend requests sent to id: ', friend_request_sent_set)


	# Return dictionary of user_id from whom they have received friend_request but have not accepted it
	friend_request_received_set = set()
	all_received_request = db.execute(
		'SELECT * FROM friendrequest'
		' WHERE user_id = ? AND friend_type_request = ?', (g.user['id'], 1)
	).fetchall()

	print('All friend request recieved: ', all_received_request)
	for item in all_received_request:
		friend_request_received_set.add(item['friend_id'])
	print('Friend request received set: ', friend_request_received_set)

	# Return dictionary of user_id of those people who are friends
	all_friends = db.execute(
		'SELECT * FROM friendrequest'
		' WHERE user_id = ? AND friend_type_request = ?', (g.user['id'], 2)
	).fetchall()

	friend_set = set()

	# print('All friends keys: ', all_friends[0].keys())
	for friend in all_friends:
		tuple_result = (friend['id'], friend['user_id'], friend['friend_id'], friend['friend_type_request'])
		print('Friend values: ', tuple_result)
		friend_set.add(friend['friend_id'])

	return friend_set, friend_request_sent_set, friend_request_received_set


def accept_friend_request(db, user_1, user_2, operation_type):
	'''
	Accepts friend request and stores them as friends in database
	'''
	db.execute(
		'INSERT INTO friendrequest (user_id, friend_id, friend_type_request)'
		' VALUES (?, ?, ?)', (user_1, user_2, operation_type)
	)
	db.commit()


def remove_friend_request(db, user_1, user_2, operation_type):
	'''
	Removes friend request from database
	'''
	db.execute(
		'DELETE FROM friendrequest'
		' WHERE user_id = ? AND friend_id = ? AND friend_type_request = ?' ,(user_1, user_2, operation_type)
	)
	db.commit()


def handle_index_post(request, db):
	'''
	Handles the post request associated with the user portal
	'''
	error = None
	print('Request from handle_index_post: ', request)
	key = list(request)[0]
	value = request[key].lower()
	operation_id = int(key.split('_')[1])
	print('Key: ', key)
	print('Value: ', value)
	print('Operation id: ', operation_id)

	# If the request is to accept a friend request
	if value == 'accept':
		# 1. Must add it to the database of the current user by setting friend_type_request = 2
		# print('We are in accept!')
		accept_friend_request(db, g.user['id'], operation_id, 2)

		# 2. Must add it to the database of the user who sent the friend request by setting
		# 	friend_type_request = 2
		accept_friend_request(db, operation_id, g.user['id'], 2)
		
		# 3. Must remove the friendrequest from the current user where friend_type_request = 1
		remove_friend_request(db, g.user['id'], operation_id, 1)

		# 4. Must remove the friendrequest from the user who sent the friend request where 
		# 	friend_type_request = 0
		remove_friend_request(db, operation_id, g.user['id'], 0)

		error = 'Friend Request Accepted!'
		flash(error)

	# If the request is to reject a friend request
	elif value == 'reject':
		print('We are in reject!')
		# Remove the friend request from the person who has received the request
		remove_friend_request(db, g.user['id'], operation_id, 1)
		# Remove the friend request from the person who has sent the request
		remove_friend_request(db, operation_id, g.user['id'], 0)

		error = 'Friend Request Declined!'
		flash(error)

	# If the request is to remove a friend 

	# If the request is to send a friend request








@bp.route('/', methods = ('GET', 'POST'))
def index():
	error = None
	db = get_db()
	if request.method == 'POST':
		print('Request form: ', request.form)
		handle_index_post(request.form, db)
		return redirect(url_for('category.index'))
	else:
		# Showing all the users on the platform that is not the current user
		print('User id: ', g.user['id'])
		all_users = db.execute(
			'SELECT username, id from user'
			' WHERE id!= ?', (g.user['id'],)
		).fetchall()

		if(len(all_users) == 0):
			flash('No other users on the platform! Check back later!')
			return redirect(url_for('category.index'))
		else:
			friend_set, friend_request_sent_set, friend_request_received_set = display_buttons(db)
			print('Friend Set: ', friend_set)

		return render_template('user/index.html', all_users = all_users, friend_set = friend_set, friend_request_sent_set = friend_request_sent_set, friend_request_received_set = friend_request_received_set)
	
