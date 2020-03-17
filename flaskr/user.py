from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('user', __name__, url_prefix = '/user')


@bp.route('/', methods = ('GET', 'POST'))
def index():
	error = None
	if request.method == 'POST':
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

		return render_template('user/index.html', all_users = all_users)
	
