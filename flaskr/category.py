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
			'create_category' : 'category/create.html',
			'remove_category' : 'category/remove.html',
			'add_expenses' : '',
			'generate_chart': '',
		}

		return render_template(possible_selection[request_type])
	return render_template('category/index.html')
