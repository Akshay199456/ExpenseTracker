from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, Markup
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import matplotlib.pyplot as plt
import random

bp = Blueprint('expense', __name__, url_prefix = '/expense')


def	generate_random_color():
	# Used to generate random hex values. Primarily used as a helper function.
	r = lambda: random.randint(0,255)
	color = '#%02X%02X%02X' % (r(),r(),r())
	print('Color: ', color)
	return color


def getPercentValues(values):
	percentValues = []
	print('Total: ', sum(values))
	for value in values:
		percentValues.append(round(100 * float(value) / float(sum(values)),  2))
	return percentValues


@bp.route('/create', methods = ('GET', 'POST'))
@login_required
def create():
	'''
	Anytime you want to create a new expense that's part of a category, this 
	function will be called. It is located at the expense.create address.
	'''
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


@bp.route('/view', methods = ('GET', 'POST'))
@login_required
def view():
	'''
	Anytime you want to view all the expenses associated with a user, the view
	function is called. Located at the expense.view address.
	'''
	db = get_db()
	error = None

	if request.method == 'POST':
		print('We are in view.post')
		print('Request form: ', request.form)

		key = list(request.form)[0]
		value = request.form[key].lower()
		operation_id = int(key.split('_')[1])
		print('Key: ', key, ' Value: ', value, 'Id: ', operation_id)
		
		if value == 'delete':
			error = 'Expense has been deleted'
			flash(error)

			db.execute(
				'DELETE FROM expense'
				' WHERE user_id = ? AND id = ?', (g.user['id'], operation_id)
			)
			db.commit()

		elif value == 'update':
			print('We are in update')
			return redirect(url_for('expense.update', operation_id = operation_id))

		return redirect(url_for('category.index'))

	else:
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




@bp.route('/update/<int:operation_id>', methods = ('GET', 'POST'))
@login_required
def update(operation_id):
	'''
	This method is called when you want to modify a particular expense
	'''
	print('We are in the update route')
	error = None
	db = get_db()
	current_expense = db.execute(
		'SELECT e.id, e.category_id, e.user_id, e.value, c.type'
		' FROM expense e JOIN category c ON e.category_id = c.id'
		' WHERE e.user_id = ? AND e.id = ?', (g.user['id'], operation_id)
	).fetchone()

	if request.method == 'POST':
		print('We are in POST section')
		print('Request form value: ', request.form['value'])

		if(request.form['value']):
			int_value = int(request.form['value'])
			print('Number entered', int_value)
			error = 'Expense has been successfully modified'
			flash(error)
			db.execute(
				'UPDATE expense SET value = ?'
				' WHERE id = ? AND user_id = ?', (int_value, operation_id, g.user['id'])
			)
			db.commit()
		else:
			error = 'No value entered. Please enter a number'
			flash(error)

		return redirect(url_for('category.index'))

	else:
		print('Current expense: ', current_expense)
		if current_expense is None:
			error = 'No valid expense is associated with the user account!'
			flash(error)
			return redirect(url_for('category.index'))
		else:
			return render_template('expense/update.html', operation_id = operation_id, current_expense = current_expense)


@bp.route('/chart/<report_type>')
@login_required
def chart(report_type):
	'''
	Anytime you want to see the chart of expenses across either debit or credit expenses, the
	chart function is called. Located at the expense.chart address. 
	'''
	error = None
	db = get_db()

	if(report_type == 'credit_report'):
		expenses = db.execute(
			'SELECT e.category_id, c.type, SUM(e.value) AS total'
			' FROM expense e JOIN category c ON e.category_id = c.id'
			' WHERE e.user_id = ? AND e.value >= 0'
			' GROUP BY e.category_id', (g.user['id'],)
		).fetchall()

	elif(report_type == 'debit_report'):
		expenses = db.execute(
			'SELECT e.category_id, c.type, SUM(e.value) AS total'
			' FROM expense e JOIN category c ON e.category_id = c.id'
			' WHERE e.user_id = ? AND e.value < 0'
			' GROUP BY e.category_id', (g.user['id'],)
		).fetchall()

	if len(expenses) == 0:
		if(report_type == 'credit_report'):		
			error = "No credit expenses have been added yet. Thus, can't generate credit report!"
		elif(report_type == 'debit_report'):
			error = "No debit expenses have been added yet. Thus, can't generate debit report!"

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
			values.append(abs(current_expense['total']))
			colors.append(generate_random_color())
		print('All labels: ', labels)
		print('All values: ', values)
		print('All colors: ', colors)
		percent_values = getPercentValues(values)
		return render_template('expense/chart.html', report_type = report_type ,labels = labels, colors = colors, values = values, percent_values = percent_values, ranges = range(len(labels)))


@bp.route('/report', methods = ('GET', 'POST'))
@login_required
def report():
	'''
	Provides the user the ability to view his credit and debit report
	'''
	if request.method == 'POST':
		print('Request form at report route: ', request.form)
		return redirect(url_for('expense.chart', report_type = request.form['submit_button']))
	else:
		return render_template('expense/report.html');

