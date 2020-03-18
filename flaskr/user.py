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
	friend_request_sent = set()
	for item in all_friend_request_sent:
		friend_request_sent.add(item['friend_id'])
	print('Friend requests sent to id: ', friend_request_sent)

	invite_set = set()

	for id in friend_request_sent:
		print('Id: ', id)
		friend_request_received = db.execute(
			'SELECT * FROM friendrequest'
			' WHERE user_id = ? AND friend_type_request = ? AND friend_id = ?', (id, 1, g.user['id'])
		).fetchone()

		print('Friend request received: ', friend_request_received)

		if len(friend_request_received) == 0:
			error = 'No friend request has been recieved!'
			flash(error)
		else:
			invite_set.add(id)
			print('Invite set: ', invite_set)


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

	return friend_set, invite_set









@bp.route('/', methods = ('GET', 'POST'))
def index():
	error = None
	if request.method == 'POST':
		print('Request form: ', request.form)
		return 'We are in user post route!'
	else:
		# Showing all the users on the platform that is not the current user
		print('User id: ', g.user['id'])
		db = get_db()
		all_users = db.execute(
			'SELECT username, id from user'
			' WHERE id!= ?', (g.user['id'],)
		).fetchall()

		if(len(all_users) == 0):
			flash('No other users on the platform! Check back later!')
			return redirect(url_for('category.index'))
		else:
			friend_set, invite_set = display_buttons(db)
			print('Friend Set: ', friend_set)

		return render_template('user/index.html', all_users = all_users, friend_set = friend_set, invite_set = invite_set)
	
