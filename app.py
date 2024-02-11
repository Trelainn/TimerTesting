from flask import (Flask, Blueprint, flash, g, render_template, request, url_for, session, redirect, send_file, Response)
from database import get_db
from multiprocessing import Manager
from os import environ 

app = Flask(__name__)

current_status = Manager().dict()

current_status['temperature'] = 0
current_status['humidity'] = 0
current_status['battery_percentage'] = 0

current_status['board_connection'] = False
current_status['antenna_connection'] = False
current_status['camera_connection'] = False

current_status['race_status'] = 'no race'


@app.route('/status', methods=['GET'])
def status():
    return str(current_status)

@app.route('/key', methods=['GET'])
def key():
    try:
        key = environ.get('KEY')
    except Exception:
        key = 'No key found'
    return key

@app.route('/update_status', methods=['POST'])
def update_status():

    current_status['temperature'] = request.json['temperature']
    '''
    current_status['battery_percentage'] = request.json['battery_percentage']
    current_status['humidity'] = request.json['humidity']
    current_status['board_connection'] = request.json['board_connection']
    current_status['antenna_connection'] = request.json['antenna_connection']
    current_status['camera_connection'] = request.json['camera_connection']
    '''
    return current_status
