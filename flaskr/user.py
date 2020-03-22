from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('user', __name__, url_prefix = '/user')


# Helper Functions

def display_buttons(db):
	'''
	Displays the appropriate buttons depending on the kind of friend request
	Currently have four different type of requests:
		1. 'Send Request' -> sends a friend request to the user
		2. 'Request Sent' -> user has already sent a friend request to the appropriate user
							but has not been accepted yet
		3. 'Friend' -> Friend Request has been accepted
		4. 'Remove' -> Removes the current friend
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
	Does one of two things:
	1. Removes friend request from database 
	2. Removes friend from database
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
		print('We are in accept!')
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
	elif value == 'remove':
		print('We are in remove!')
		# Remove the friend from the current user
		remove_friend_request(db, g.user['id'], operation_id, 2)
		# Remove the current user from the friend
		remove_friend_request(db, operation_id, g.user['id'], 2)

		error = 'Friend Removed!'
		flash(error)

	# If the request is to send a friend request
	elif value == 'send':
		print('We are in send!')
		# Must send friend request to the user from the current user
		accept_friend_request(db, g.user['id'], operation_id, 0)
		# The other user must have an invitation to accept from the current user
		accept_friend_request(db, operation_id, g.user['id'], 1) 

		error = 'Friend Request Sent!'
		flash(error)


def get_current_user_username(db, user_id):
	''' Gets the username associated with the current user'''
	current_user = db.execute(
		'SELECT username from user'
		' WHERE id = ?', (user_id,)
	).fetchone()

	return current_user['username']



def insert_transaction(db, user_id, friend_id, request_type, amount):
	'''
	Inserts a transaction to the database
	'''
	db.execute(
		'INSERT INTO transactionrequest (user_id, friend_id, request_type, amount)'
		' VALUES (?, ?, ?, ?)', (user_id, friend_id, request_type, amount)
	)
	db.commit()


def delete_transaction(db, id):
	'''
	Deletes a transaction given the id of the transaction
	'''
	db.execute(
		'DELETE FROM transactionrequest'
		' WHERE id = ? ', (id, )
	)
	db.commit()


def select_first_matched_transaction(db, user_id, friend_id, request_type, amount):
	'''
	Selects only the first instance of the transaction to delete from the database
	'''
	first_match = db.execute(
		'SELECT * FROM transactionrequest'
		' WHERE user_id = ? AND friend_id = ? AND request_type = ? AND amount = ?', (user_id, friend_id, request_type, amount)
	).fetchone()
	return first_match


def check_category_exists_and_create(db, category, user_id, amount, kind):
	'''
	1. Checks if the category exist or not.
	2. If it doesn't exist, the category is created
	3. Get the id associated with the category created
	4. If the transaction kind is debit, you want to negate the amount value
	5. Adds the expense to the user
	'''
	is_category = db.execute(
		'SELECT * from category'
		' WHERE type = ? AND user_id = ?',(category, user_id) 
	).fetchone()
	
	# If it does, we create a new expense and add it with that category to the user
	if is_category:
		print('Category exists')

	# If it doesn't:
	else:
		print("Category doesn't exist!")
				
		## Create that category for the current user
		db.execute(
			'INSERT INTO category (user_id, type)'
			' VALUES (?, ?)', (user_id, category)
		)
		db.commit() 

	# Get the id associated with the category
	current_category = db.execute(
		'SELECT * FROM category'
		' WHERE type = ? AND user_id = ?', (category, user_id)
	).fetchone()

	# Create a new expense and add it to that category for the current user
	if kind == 'debit':
		amount = -1 * amount

	db.execute(
		'INSERT INTO expense (category_id, user_id, value)'
		' VALUES (?, ?, ?)', (current_category['id'], user_id, amount)
	)
	db.commit()








# Routes


@bp.route('/', methods = ('GET', 'POST'))
def index():
	print('We are in index route!')
	error = None

	if request.method == 'POST':
		option = request.form['submit_button'].lower()
		print('Option: ', option)

		if option == 'all users':
			return redirect(url_for('user.view'))
		elif option == 'friends':
			return redirect(url_for('user.friend'))
	else:
		return render_template('user/index.html')


@bp.route('/friend', methods = ('GET', 'POST'))
def friend():
	error = None
	db = get_db()
	print('We are in friend route')
	if request.method == 'POST':
		print('Request form: ', list(request.form))
		key = list(request.form)[0]
		transaction_type = request.form[key].lower()
		friend_id = int(key.split('_')[1])

		print('Key: ', key)
		print('Value: ', transaction_type)
		print('Id: ', friend_id)
		return redirect(url_for('user.transaction', friend_id = friend_id, transaction_type = transaction_type, user_id = g.user['id']))
	else:	
		all_friends = db.execute(
			'SELECT f.user_id, f.friend_id, f.friend_type_request, u.username'
			' FROM friendrequest f JOIN user u ON f.friend_id = u.id'
			' WHERE f.user_id = ? AND f.friend_type_request = ?', (g.user['id'], 2)
		).fetchall()
		print('All friends: ', all_friends)
		
		if not all_friends:
			error = 'You currently have no friends! Add friends to exchange money.'
			flash(error)
	return render_template('user/friends.html', all_friends = all_friends)



@bp.route('/transaction/<int:friend_id>/<transaction_type>/<int:user_id>', methods = ('GET', 'POST'))
def transaction(friend_id, transaction_type, user_id):
	error = None
	print('Friend id: ', friend_id)
	print('Transaction type: ', transaction_type)
	print('User id: ', user_id)
	if request.method == 'POST':
		print('Request form: ', request.form)
		amount = int(request.form['amount'])
		print('Amount: ', amount)
		db = get_db()

		if transaction_type == 'send':
			print('We are in send')
			insert_transaction(db, g.user['id'], friend_id, 10, amount)
			insert_transaction(db, friend_id, g.user['id'], 40, amount)
			error = 'Request to send money has been sent!'
		elif transaction_type == 'request':
			print('We are in request')
			insert_transaction(db, g.user['id'], friend_id, 20, amount)
			insert_transaction(db, friend_id, g.user['id'], 30, amount)
			error = 'Request to receive money has been sent!'

		flash(error)
		return redirect(url_for('user.friend'))

	else:
		return render_template('user/transaction.html', friend_id = friend_id, transaction_type = transaction_type, user_id = g.user['id'])



@bp.route('/view', methods = ('GET', 'POST'))
def view():
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

		return render_template('user/view.html', all_users = all_users, friend_set = friend_set, friend_request_sent_set = friend_request_sent_set, friend_request_received_set = friend_request_received_set)


@bp.route('/sent')
def sent():
	db = get_db()
	# Get transactions that have request_type = 10, 11, 20, 21
	sent_transactions = db.execute(
		'SELECT t.user_id, t.friend_id, t.request_type, t.amount, u.username'
		' FROM transactionrequest t JOIN user u'
		' ON t.friend_id = u.id'
		' WHERE t.user_id = ?'
		' AND (t.request_type = ? OR t.request_type = ?)',
		(g.user['id'], 10, 20)
	).fetchall()

	print('Sent transactions: ', sent_transactions)
	current_username = get_current_user_username(db, g.user['id'])
	print('Current user username: ', current_username)

	# Need to resume writing code from here by modifying the sent.html file to make the 
	# transactions appear the intended way
	return render_template('user/sent.html', type = 'sent', sent_transactions = sent_transactions, current_username = current_username)

	


@bp.route('/received', methods = ('GET', 'POST'))
def received():
	error = None
	db = get_db()
	# Get transactions that have request_type = 30, 31, 40, 41
	if request.method == 'POST':
		print('Request form: ', request.form)
		key = list(request.form)[0]
		value = request.form[key]
		tokens = key.split('_')
		print('Key: ', key)
		print('Value: ', value)
		print('Tokens:', tokens)
		transaction_method = tokens[0]
		transaction_type = int(tokens[1])
		transaction_friend_id = int(tokens[2])
		transaction_amount = int(tokens[3])
		print('Transaction variables: ', transaction_method, transaction_type, transaction_friend_id, transaction_amount)


		# Need to check if the user accepted or rejected the request
		if value == 'Reject':
			print('User clicked on reject')
			# If the user rejected the request: 
			
			## get only the first instance of the transaction type
			first_match = select_first_matched_transaction(db, g.user['id'], transaction_friend_id, transaction_type, transaction_amount)
			print('Current transaction: ', first_match)
			print(first_match['id'], first_match['user_id'], first_match['friend_id'], first_match['request_type'], first_match['amount'])

			## remove the transaction from the current user's database
			delete_transaction(db, first_match['id'])	


			# remove only the first instance of the transaction from the other user's database
			if transaction_type == 30:
				remove_transaction_type = 20
			elif transaction_type == 40:
				remove_transaction_type = 10

			## get only the first instance of the transaction
			return_match = select_first_matched_transaction(db, transaction_friend_id, g.user['id'], remove_transaction_type, transaction_amount)  
			## remove the transaction from the current user's database 
			delete_transaction(db, return_match['id'])


			## Add the transaction for the current user to completed rejected transaction depending 
			## on whether it was a send/receive request to the database
						#    AND
			# Add the transaction for the other user to complete rejected depending on whether
			# it was a receive/send request to the database

			if first_match['request_type'] == 30:
				insert_transaction(db, g.user['id'], transaction_friend_id, 71, first_match['amount'])
				insert_transaction(db, transaction_friend_id, g.user['id'], 80, first_match['amount'])
			elif first_match['request_type'] == 40:
				insert_transaction(db, g.user['id'], transaction_friend_id, 81, first_match['amount'])
				insert_transaction(db, transaction_friend_id, g.user['id'], 70, first_match['amount'])

			error = 'Transaction request has been rejected!'
			flash(error)


		# else if the user accepted the request:
		elif value == 'Accept':
			print('User clicked on accept')
			## Get the name of the person sending the request
			friend_username = get_current_user_username(db, transaction_friend_id)
			print('Friend username: ', friend_username)

			## Need to check if category - 'Credit/Debit: {{friend_username}} exists' for the current user
			if transaction_type == 30:
				category_user = 'DEBIT (' + friend_username + ')'
				kind_user = 'debit'

				category_friend = 'CREDIT (' + get_current_user_username(db, g.user['id']) +')'
				kind_friend = 'credit'

			elif transaction_type == 40:
				category_user = 'CREDIT (' + friend_username + ')'
				kind_user = 'credit'

				category_friend = 'DEBIT (' + get_current_user_username(db, g.user['id']) + ')'
				kind_friend = 'debit'

			## Checks and adds categories 
			check_category_exists_and_create(db, category_user, g.user['id'], transaction_amount, kind_user)
			check_category_exists_and_create(db, category_friend, transaction_friend_id, transaction_amount, kind_friend)




			# Remove the transaction from the current user as well as friend and push it as a completed
			# transaction to both the current user and the friend

			## get only the first instance of the transaction type for the current user
			first_match = select_first_matched_transaction(db, g.user['id'], transaction_friend_id, transaction_type, transaction_amount)
			print('Current transaction: ', first_match)
			print(first_match['id'], first_match['user_id'], first_match['friend_id'], first_match['request_type'], first_match['amount'])

			## remove the transaction from the current user's database
			delete_transaction(db, first_match['id'])	


			# remove only the first instance of the transaction from the other user's database
			if transaction_type == 30:
				remove_transaction_type = 20
			elif transaction_type == 40:
				remove_transaction_type = 10

			## get only the first instance of the transaction for the friend
			return_match = select_first_matched_transaction(db, transaction_friend_id, g.user['id'], remove_transaction_type, transaction_amount)  
			## remove the transaction from the current user's database 
			delete_transaction(db, return_match['id'])


			## Add the transaction for the current user to completed rejected transaction depending 
			## on whether it was a send/receive request to the database
						#    AND
			# Add the transaction for the other user to complete rejected depending on whether
			# it was a receive/send request to the database

			if first_match['request_type'] == 30:
				insert_transaction(db, g.user['id'], transaction_friend_id, 51, first_match['amount'])
				insert_transaction(db, transaction_friend_id, g.user['id'], 60, first_match['amount'])
			elif first_match['request_type'] == 40:
				insert_transaction(db, g.user['id'], transaction_friend_id, 61, first_match['amount'])
				insert_transaction(db, transaction_friend_id, g.user['id'], 50, first_match['amount'])

			error = 'Transaction request has been accepted!'
			flash(error)

		return redirect(url_for('user.received'))

	else:
		received_transactions = db.execute(
			'SELECT t.user_id, t.friend_id, t.request_type, t.amount, u.username'
			' FROM transactionrequest t JOIN user u'
			' ON t.friend_id = u.id'
			' WHERE t.user_id = ?'
			' AND (t.request_type = ? OR t.request_type = ?)',
			(g.user['id'], 30, 40)
		).fetchall()

		print('Received transactions: ', received_transactions)
		current_username = get_current_user_username(db, g.user['id'])
		print('Current user username: ', current_username)
		return render_template('user/received.html', type = 'received', received_transactions = received_transactions, current_username = current_username)


@bp.route('/completed')
def completed():
	# Get transactions that have request_type = 50, 51, 60, 61, 70, 71, 80, 81
	error = None
	db = get_db()
	completed_transactions = db.execute(
		'SELECT t.user_id, t.friend_id, t.request_type, t.amount, u.username'
		' FROM transactionrequest t JOIN user u'
		' ON t.friend_id = u.id'
		' WHERE t.user_id = ?'
		' AND (t.request_type = ? OR t.request_type = ? OR t.request_type = ? OR t.request_type = ? OR t.request_type = ? OR t.request_type = ? OR t.request_type = ? OR t.request_type = ?)',
		(g.user['id'], 50, 51, 60, 61, 70, 71, 80, 81)
	).fetchall()
	print('Completed transactions: ', completed_transactions)
	current_username = get_current_user_username(db, g.user['id'])
	print('Current user username: ', current_username)
	return render_template('user/completed.html', type = 'completed', completed_transactions = completed_transactions, current_username = current_username)