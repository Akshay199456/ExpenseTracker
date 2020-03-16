# Define the blueprint and register it in the application factory.

from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('category', __name__)

@bp.route('/', methods = ('GET', 'POST'))
def index():
	'''
	Serves as the home route when the user logs in. Shows all the possible 
	selections available to the user. Exists at the category.index address.
	'''
	if request.method == 'POST':
		print("Request: ", request.form)
		error = None
		request_type = request.form['submit_button']

		possible_selection = {
			'set_budget' : 'expense.budget',
			'create_category' : 'category.create',
			'remove_category' : 'category.delete',
			'add_expenses' : 'expense.create',
			'view_expenses' : 'expense.view',
			'generate_chart': 'expense.report',
		}
		# Need to redirect to proper link on click
		# return render_template(possible_selection[request_type])
		return redirect(url_for(possible_selection[request_type]))
	return render_template('category/index.html')

@bp.route('/create', methods = ('GET', 'POST'))
@login_required
def create():
	'''
	Anytime you want to create a new categoy, this method is called. Exists
	at the category.create address.
	'''
	if request.method == 'POST':
		print('Request form: ', request.form)
		error = None
		category_type = request.form['category'].title()

		if not category_type:
			error = 'Category type is required!'
		
		if error is not None:
			flash(error)
		else:
			db = get_db()
			existing_category = db.execute(
				'SELECT c.id, c.type, c.user_id'
				' FROM category c JOIN user u ON c.user_id = u.id'
				' WHERE c.type = ? AND c.user_id = ?',(category_type, g.user['id'])
			).fetchone()

			print('Does category exist: ', existing_category)
			if existing_category is not None:
				error = 'Category ' + category_type + ' already exists!'
				flash(error)
			else:
				print('Current user id: ', g.user['id'])
				db.execute(
					'INSERT INTO category (type, user_id)'
					' VALUES (?, ?)', (category_type, g.user['id'])
				)
				db.commit()
				return redirect(url_for('category.index'))
	return render_template('category/create.html')


@bp.route('/delete', methods = ('GET', 'POST'))
@login_required
def delete():
	'''
	Anytime you want to delete a category, this function is called. Exists
	at the category.delete address
	'''
	if request.method == 'POST':
		error = None
		print('Request form: ', request.form)
		category_type = request.form['category'].title()

		if not category_type:
			error = 'Category type is required!'
			flash(error)
		else:
			db = get_db()
			check_category = db.execute(
				'SELECT id, type, user_id'
				' FROM category'
				' WHERE type = ? AND user_id = ?', (category_type, g.user['id'])
			).fetchone()

			print('Does category exist: ', check_category)
			
			if check_category is None:
				error = "Category " + category_type + " doesn't exist!"
				flash(error)
				print('User id: ', g.user['id'])
				return redirect(url_for('category.delete'))
			
			# Must add another condition to check if the category that you are trying to use
			# has more than one expense associated with it. If it has, we can't delete it till
			# expenses are modified
			else:
				check_expense_exists = db.execute(
					'SELECT *'
					' FROM expense'
					' WHERE category_id = ?', (check_category['id'],)
				).fetchone()
				print('Check expense exists: ', check_expense_exists, ' category_id: ', check_category['id'])
				
				if check_expense_exists is not None:
					error = "Expenses are associated with " + check_category['type'] +'. They must be deleted before the category can be removed!'
					flash(error)
					print('User id: ', g.user['id'])
					return redirect(url_for('category.delete'))

				else:
					error = 'Category ' + category_type + ' has been removed!'
					flash(error)
					db.execute(
						'DELETE FROM category'
						' WHERE type = ? AND user_id = ?', (category_type, g.user['id'])
					)
					db.commit()
			return redirect(url_for('category.index'))
	return render_template('category/remove.html')

