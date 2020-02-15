from flask import Flask, render_template, url_for
app = Flask(__name__)

@app.route('/')
def helloWorld():
	return render_template('index.html')

@app.route('/expenses')
def expenses():
	return render_template('render.html')

if(__name__ == '__main__'):
	app.run()