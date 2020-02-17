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
	if request.method == 'POST':
		print("Request: ", request.form)
		error = None
		request_type = request.form['submit_button']

		possible_selection = {
			'create_category' : 'category.create',
			'remove_category' : 'category.remove',
			'add_expenses' : 'category.addExpenses',
			'generate_chart': 'category.chart',
		}
		# Need to redirect to proper link on click
		# return render_template(possible_selection[request_type])
		return redirect(url_for(possible_selection[request_type]))
	return render_template('category/index.html')

@bp.route('/create', methods = ('GET', 'POST'))
@login_required
def create():
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

