import psycopg2
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
	db = psycopg2.connect(	
		host = 'localhost',
		user = 'postgres',
		password = 'Soporte1.',
		database = 'seabob')
	c = db.cursor()
	return db, c	

def close_db(e=None):
	db = g.pop('db', None)
	if db is not None:
		db.close()

def init_app(app):
	app.teardown_appcontext(close_db)