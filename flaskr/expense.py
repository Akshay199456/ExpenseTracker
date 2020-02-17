from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('expense', __name__, url_prefix = '/expense')

@bp.route('/create', methods = ('GET', 'POST'))
@login_required
def create():
	db = get_db()
	error = None
	if request.method == 'POST':
		pass
	else:
		categories = db.execute(
			'SELECT * FROM category'
			' WHERE user_id = ?', (g.user['id'],)
		).fetchall()

		if len(categories) == 0:
			error = 'Need to first create atleast 1 category before an expense can be inserted!'
			flash(error)
			return redirect(url_for('category.index'))
		else:
			'''
			print('Categories: ', categories)
			for category in categories:
				print('*********************')
				print('Id: ', category['id'])
				print('User id: ', category['user_id'])
				print('Type: ', category['type'])
				print('*********************')
			'''
			return render_template('expense/create.html', categories = categories)

