from flask import (Flask, Blueprint, flash, g, render_template, request, url_for, session, redirect, send_file, Response)
from database import get_db
from multiprocessing import Manager
from os import environ 
from pathlib import Path
from datetime import datetime
import string
import random

app = Flask(__name__)

def get_current_status():
    db, c = get_db()
    c.execute(
        'select * from system_tracker order by id DESC'
    )
    system_tracker = c.fetchone()
    current_status = {}
    if system_tracker is not None:
        current_status['id'] = system_tracker[0]
        current_status['date'] = system_tracker[1]
        current_status['battery_percentage'] = system_tracker[2]
        current_status['temperatrue'] = system_tracker[3]
        current_status['race_status'] = system_tracker[4]
        current_status['race_number'] = system_tracker[5]
        current_status['camera_on'] = system_tracker[6]
        current_status['antenna_on'] = system_tracker[7]
        current_status['pcb_connection'] = system_tracker[8]
        current_status['internet_available'] = system_tracker[9]
        current_status['led_status'] = system_tracker[10]
    return current_status 

def get_system_parameters():
    db, c = get_db()
    c.execute(
        'select * from system_parameters order by id ASC'
    )
    system_paramters = c.fetchall()
    current_status = {}
    if system_paramters is not None:
        current_status['race_status'] = system_paramters[1][1]
        current_status['next_race_number'] = int(system_paramters[0][1])
    return current_status 

def update_system_parameters(race_number, race_status, user_id):
    db, c = get_db()
    c.execute(
        'update system_parameters set value = %s where id = %s', (race_number + 1, 'next_race_number')
    )
    c.execute(
        'update system_parameters set value = %s where id = %s', (race_status, 'race_status')
    )
    c.execute(
        'update system_parameters set value = %s where id = %s', (user_id, 'race_owner')
    )
    db.commit()

def get_race_info(race_number, user_id):
    db, c = get_db()
    c.execute('select * from races where race_number = %s', (race_number, ))
    race = c.fetchone()
    race_info = {}
    race_info['race_number'] = race_number
    if race is not None:
        race_info['code'] = race[1]
        race_info['user_id'] = race[2]
        race_info['status'] = race[3]
        race_info['track'] = race[4]
        race_info['race_type'] = race[5]
        race_info['limit_number'] = race[6]
        if  race_info['status'] == 'finished':
            race_info['race_time'] = (race[8] - race[7]).seconds
        if race[7] is not None:
            race_info['race_time'] = (race[7]).seconds
        else:
            race_info['race_time'] = 0
        race_info['race_competitors'] = []
        c.execute('select tag from race_competitors where race_number = %s', (race_number, ))
        race_competitors = c.fetchall()
        for competitor in race_competitors:
            race_info['race_competitors'].append(get_competitor_info(race_number=race_number, tag=competitor[0], user_id=user_id))
        race_info['race_competitors_amount'] = len(race_info['race_competitors'])
    return race_info

def get_competitor_info(race_number, tag, user_id):
    db, c = get_db()
    c.execute('select * from race_competitors where race_number = %s and tag = %s', (race_number, tag))
    competitor = c.fetchone()
    competitor_info = {}
    competitor_info['race_number'] = race_number
    competitor_info['tag'] = tag
    if competitor is not None:
        competitor_info['nickname'] = competitor[2]
        competitor_info['user_id'] = competitor[3]
        competitor_info['toy'] = competitor[4]
        competitor_info['gender'] = competitor[5]
        competitor_info['weight_category'] = competitor[6]
        competitor_info['photo'] = competitor[7]
        if competitor_info['photo']:
            competitor_info['photo_url'] = url_for('profile_photo', race_number=race_number, tag=tag)
        competitor_info['video_permission'] = competitor[8]
        if competitor_info['video_permission'] and competitor_info['user_id'] == user_id:
            competitor_info['laps'] = get_laps_info(race_number, tag, True, user_id)
        else:
            competitor_info['laps'] = get_laps_info(race_number, tag, False, user_id)
    return competitor_info

def get_laps_info(race_number, tag, video_permission, user_id):
    db, c = get_db()
    c.execute('select * from race_competitors_laps where race_number = %s and tag = %s order by ASC', (race_number, tag))
    competitor_laps = c.fetchall()
    competitor_laps_info = {}
    competitor_laps_info['race_number'] = race_number
    competitor_laps_info['tag'] = tag
    competitor_laps_info['video_permission'] = video_permission
    competitor_laps_info['best_lap'] = -1
    competitor_laps_info['best_time'] = -1
    competitor_laps_info['laps_amount'] = 0
    competitor_laps_info['laps'] = []
    if competitor_laps is not None:
        for competitor_lap in competitor_laps:
            lap = {}
            lap['lap'] = competitor_lap[2]
            lap['time'] = competitor_lap[3]/1000
            if lap['time'] < competitor_laps_info['best_time'] or competitor_laps_info['best_time'] == -1:
                competitor_laps_info['best_time'] = lap['time']
                competitor_laps_info['best_lap'] =  lap['lap']
            if video_permission:
                lap['video_name'] = competitor_lap[4]
                lap['video_url'] = url_for('video', race_number=race_number, tag=tag, lap=competitor_lap[2], user_id=user_id)
            lap['info_uploaded'] = competitor_lap[5]
            lap['video_uploaded'] = competitor_lap[6]
            competitor_laps_info['laps'].append(lap)
    return competitor_laps_info

def get_video_info(race_number, tag, lap, user_id):
    db, c = get_db()
    c.execute('select * from race_competitors_laps where race_number = %s and tag = %s and lap = %s', (race_number, tag, lap))
    lap = c.fetchone()
    c.execute('select * from race_competitors where race_number = %s and tag', (race_number, tag))
    race_competitors_user_id = c.fetchone()[3]
    lap_info = {}
    lap_info['race_number'] = race_number
    lap_info['tag'] = tag
    lap_info['lap'] = lap
    lap_info['user_id'] = user_id 
    if lap is not None and race_competitors_user_id is not None:
        lap_info['owner_user_id'] = race_competitors_user_id 
        lap_info['time'] = lap[3]/1000
        lap_info['video_name'] = lap[4]
        if lap_info['video_name'] != '' and user_id == race_competitors_user_id:
            lap_info['video_available'] = True
        else: 
            lap_info['video_available'] = False
        lap_info['info_uploaded'] = lap[5]
        lap_info['video_uploaded'] = lap[6] 
    return lap_info
@app.route('/status', methods=['GET'])
def status():
    return get_current_status()

@app.route('/system_parameters', methods=['GET'])
def system_parameters():
    return get_system_parameters()

@app.route('/create_race', methods=['POST'])
def create_race():
    status = get_system_parameters()
    try:
        if status['race_status'] == 'no race':
            user_id = request.json['user_id']
            race_code = ''.join(random.choice(string.ascii_uppercase) for x in range(4))
            race_number = status['next_race_number']
            race_status = 'configure_race'
            db, c = get_db()
            c.execute(
                'insert into races (race_number, user_id, code, race_status) values (%s, %s, %s, %s)', (race_number , user_id, race_code, race_status)
			)
            update_system_parameters(race_number=race_number+1, race_status=race_status, user_id=user_id)
            db.commit()
            return {'ok': True, 'process': 'Start race', 'status': 'success'}
        else:
            return {'ok': False, 'process': 'Start race', 'status': 'failed', 'error': 'race already created'}
    except Exception as e: 
        return {'ok': False, "error": str(e)}    

@app.route('/select_track', methods=['POST'])
def select_track():
    status = get_system_parameters()
    user_id = request.json['user_id']
    try:
        if status['race_status'] == 'configure_race' and status['race_owner'] == user_id:
            db, c = get_db()
            c.execute(
                'update races set track = %s where race_number = %s', (request.json['track'], status['next_race_number']-1)
			)
            db.commit()
            return {'ok': True, 'process': 'Select track', 'status': 'success'}
        else:
            return {'ok': False, 'process': 'Select track', 'status': 'failed'}
    except:
        return {'ok': False}    
    
@app.route('/race_type', methods=['POST'])
def race_type():
    status = get_system_parameters()
    user_id = request.json['user_id']
    try:
        if status['race_status'] == 'configure_race' and status['race_owner'] == user_id:
            db, c = get_db()
            c.execute(
                'update races set race_type = %s, limit_number = %s where race_number = %s', (request.json['race_type'], request.json['limit_number'], status['next_race_number']-1)
			)
            db.commit()
            return {'ok': True, 'process': 'Race type', 'status': 'success'}
        else:
            return {'ok': False, 'process': 'Race type', 'status': 'failed'}
    except:
        return {'ok': False}   
    
@app.route('/add_participant', methods=['POST'])
def add_participant():
    status = get_system_parameters()
    try:
        if status['race_status'] == 'configure_race':
            user_id = request.form['user_id']
            nickname = request.form['nickname']
            gender = request.form['gender']
            weight_category = request.form['weight_category']
            toy = request.form['toy']
            tag = request.form['tag']
            video_permission = request.form['video_permission']
            photo = request.form['photo']
            image = request.files['image']
            error_image = None
            if photo:
                try:
                    image.save(str(Path().absolute())+'/static/profile_pictures/'+str(tag)+'.jpg')
                except Exception as e:
                    error_image = e
                    print('The file could not be saved due to the following error: '+str(e))
            db, c = get_db()
            c.execute('select * from race_competitors where race_number = %s and tag = %s',(status['race_number']-1, tag))
            competitor = c.fetchone()
            if competitor is None:
                c.execute(
					'insert into race_competitors (race_number, tag, nickname, user_id, toy, gender, weight_category, photo, video_permission) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
					(status['race_number']-1, tag, nickname, user_id, toy, photo, video_permission)
				)
                message = 'New participant added'
            else:
                c.execute(
					'update race_competitors set nickname = %s, user_id = %s, toy = %s, gender = %s, weight_category = %s, photo = %s, video_permission = %s where race_number = %s and tag = %s', 
					(nickname, user_id, toy, gender, weight_category, photo, video_permission, status['race_number']-1, tag)
				)
                message = 'Participant updated'
            db.commit()
            return {'ok': True, 'status': 'success', 'process': 'Add Participant', 'message': message,  'image_error': error_image}
        else:
            return {'ok': False, 'process': 'Add Participant', 'status': 'failed'}
    except:
        return {'ok': False} 

@app.route('/start_race', methods=['POST'])
def start_race():
    status = get_system_parameters()
    user_id = request.json['user_id']
    try:
        if status['race_status'] == 'configure_race' and status['race_owner'] == user_id:
            db, c = get_db()
            c.execute(
                'update races set race_begin_time = %s, status = %s where race_number = %s', (datetime.now(), 'racing', status['race_number']-1,)
			)
            db.commit()
            return {'ok': True, 'process': 'Start Race', 'status': 'success'}
        return {'ok': False, 'process': 'Start Race', 'status': 'failed'}
    except:
        pass
    return {'ok': False, 'process': 'Start Race', 'status': 'failed'}
@app.route('/record_time/<tag>/<time>', methods=['POST'])
def record_time(tag, time):
    status = get_system_parameters()
    try:
        if status['race_status'] == 'racing':
            db, c = get_db()
            c.execute('select lap from times where tag = %s and race_number = %s order by lap desc', (tag, status['race_number']-1))
            lap_number = c.fetchone()
            c.execute('select video_permission from race_competitors where tag = %s and race_number = %s', (tag, status['race_number']-1))
            video_permission = c.fetchone()[0]
            if lap_number is not None:
                lap_number = float(lap_number[0])+ 1
            else:
                lap_number = 1
            if video_permission:
                video_name = str(status['race_number']-1)+'_'+tag+'_'+lap_number
            c.execute('insert into times (race_number, tag, lap, time_milliseconds) values (%s, %s, %s, %s)', (status['race_number']-1, tag, lap_number, time))
            db.commit()
            return {'ok': True, 'process': 'Record Time', 'status': 'success', 'race_number': status['race_number']-1, 'tag': tag, 'lap_number': lap_number, 'time':time, 'video_name': video_name, 'video_permission': video_permission}
        return {'ok': False, 'process': 'Record Time', 'status': 'failed'}
    except:
        pass
    return {'ok': False, 'process': 'Record Time', 'status': 'failed'}

@app.route('/stop_race', methods=['POST'])
def stop_race():
    status = get_system_parameters()
    user_id = request.json['user_id']
    try:
        if status['race_status'] == 'configure_race' and status['race_owner'] == user_id:
            db, c = get_db()
            c.execute(
                'update races set race_final_time = %s, status = %s where race_number = %s', (datetime.now(), 'finished', status['race_number']-1,)
			)
            db.commit()
    except:
        pass
@app.route('/view_race', methods=['POST'])
def view_race():
    user_id = request.json['user_id']
    race_number = request.json['race_number']
    system_parameters = get_system_parameters()
    return get_race_info(race_number=race_number, user_id=user_id)
    if system_parameters['race_number']-1 == race_number:
        return get_race_info(race_number=race_number, user_id=user_id)
    else:
        pass
@app.route('/video/', methods=['POST'])
def video(race_number, tag, lap, user_id):
    video_info = get_video_info(race_number=race_number, tag=tag, lap=lap, user_id=user_id)
    if video_info['video_available']:
        return send_file('/home/Trelainn/Documents/TimerTesting/static/videos/'+str(race_number)+'-'+str(tag)+'-'+str(lap)+'.mp4', as_attachment=True)
    else:
        if video_info['video_uploaded']:
            return Response("Server available", status=400,)
        return Response("No video available", status=403,)
@app.route('/profile_picture/', methods=['POST'])
def profile_picture(race_number, tag):
	return send_file('/home/Trelainn/Documents/TimerTesting/static/profile_pictures/'+str(race_number)+'_'+str(tag)+'.jpeg', as_attachment=True)

@app.route('/update_status', methods=['POST'])
def update_status():
    pass

'''
@app.route('/environment_variables', methods=['GET'])
def environment_variables():
    host = environ.get('HOST')
    user = environ.get('USER')
    password = environ.get('PASSWORD')
    database = environ.get('DATABASE')

    return {"host": host, "user":user, "password":password, "database":database}
'''
    

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=80)