import psycopg2
from flask import current_app, g
from flask.cli import with_appcontext
from os import environ 

def get_db():
	db = psycopg2.connect(	
		host = 'localhost',
		user = 'postgres',
		password = '8fnVZpx7i+RT?47',
		database = 'seamaze')
	c = db.cursor()
	return db, c	

def close_db(e=None):
	db = g.pop('db', None)
	if db is not None:
		db.close()

def init_app(app):
	app.teardown_appcontext(close_db)