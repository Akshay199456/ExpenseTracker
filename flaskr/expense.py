from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, Markup
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import matplotlib.pyplot as plt
import random

bp = Blueprint('expense', __name__, url_prefix = '/expense')

@bp.route('/create', methods = ('GET', 'POST'))
@login_required
def create():
	db = get_db()
	error = None

	if request.method == 'POST':
		'''
		print('Request form: ', request.form)
		print('Type of category: ', type(int(request.form['category'])))
		print('Type of user: ', type(g.user['id']))
		print('Type of expense: ', type(int(request.form['expense'])))
		'''
		db.execute(
			'INSERT INTO expense (category_id, user_id, value)'
			' VALUES (?, ?, ?)', (int(request.form['category']), g.user['id'], int(request.form['expense']))
		)
		db.commit()
		return redirect(url_for('category.index'))
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
			# Shows the information stored in the list
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


@bp.route('/view')
@login_required
def view():
	db = get_db()
	error = None
	
	all_expenses = db.execute(
		'SELECT e.id, e.category_id, e.user_id, e.value, c.type'
		' FROM expense e JOIN category c ON e.category_id = c.id'
		' WHERE e.user_id = ?', (g.user['id'],)
	).fetchall()

	if len(all_expenses) == 0:
		error = 'No expenses associated with your account. Please create an expense first!'
		flash(error)
		return redirect(url_for('category.index'))
	else:
		print('All expenses: ', all_expenses)
		return render_template('expense/view.html', all_expenses = all_expenses)	


@bp.route('/chart')
@login_required
def chart():
	error = None
	db = get_db()
	expenses = db.execute(
		'SELECT e.category_id, c.type, SUM(e.value) AS total'
		' FROM expense e JOIN category c ON e.category_id = c.id'
		' WHERE e.user_id = ?'
		' GROUP BY e.category_id', (g.user['id'],)
	).fetchall()

	if len(expenses) == 0:
		error = "No expenses have been added yet. Thus, can't generate user report!"
		flash(error)
		return redirect(url_for('category.index'))
	else:
		labels, values, colors = [], [], []
		print('All expenses: ', expenses)
		for expense in expenses:
			current_expense = dict(expense)
			# print("Expense: ", current_expense)
			# print("Current color: ", generate_random_color())
			labels.append(current_expense['type'])
			values.append(current_expense['total'])
			colors.append(generate_random_color())
		print('All labels: ', labels)
		print('All values: ', values)
		print('All colors: ', colors)
		return render_template('expense/chart.html', labels = labels, colors = colors, values = values)


def	generate_random_color():
	# Used to generate random hex values
	r = lambda: random.randint(0,255)
	color = '#%02X%02X%02X' % (r(),r(),r())
	print('Color: ', color)
	return color

