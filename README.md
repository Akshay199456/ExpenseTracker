# Expense Tracker Application

A few set up instructions that can help speed up the setting the server are given below:

1. Having an environment helps set up and install the dependencies really easily without having any
hassle

- To see a list of all the environments that exist using conda, use the command

> conda env list

- To activate the environment associated with this aplication use,

> conda activate expense_tracker_env

To see a complete list of the commands associated with conda, check out the [Conda Docs](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)



2. To set up the server, make sure you are in the top-level 'flask-tutorial' directory and not the 
'flaskr' package

- To setup the application in development mode

'''
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
'''

To see a complete tutorial of setting up a flask application, use the [Flask Docs](https://flask.palletsprojects.com/en/1.1.x/tutorial/factory/)



3. To connect to the sqlite3 database through the command line, make sure you are in the 'instance' sub-folder

- To connect to the database 

> sqlite3 flaskr.sqlite

There are several other commands that can be used with sqlite3. To check them over, head over to the [SQLite Docs](https://sqlite.org/cli.html#zipdb).
