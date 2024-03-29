from flask import (Flask, Blueprint, flash, g, render_template, request, url_for, session, redirect, send_file, Response)
from database import get_db
from multiprocessing import Manager
from os import environ 
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from werkzeug.utils import secure_filename
import string
import random
import time
import os
import uuid
import requests

app = Flask(__name__)
wifi_list = []
wifi_network_change_data = {'change': False}
picture_extensions = {'png', 'jpg', 'jpeg'}

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
        current_status['temperature'] = system_tracker[3]
        current_status['race_status'] = system_tracker[4]
        current_status['race_number'] = system_tracker[5]
        current_status['camera_on'] = system_tracker[6]
        current_status['antenna_on'] = system_tracker[7]
        current_status['pcb_connection'] = system_tracker[8]
        current_status['internet_available'] = system_tracker[9]
        current_status['led_status'] = system_tracker[10]
        current_status['charger_connected'] = system_tracker[11]
        current_status['starting_system'] = system_tracker[12]
        current_status['system_shut_down'] = system_tracker[13]
    return current_status 

def get_system_parameters():
    db, c = get_db()
    c.execute(
        'select * from system_parameters order by id ASC'
    )
    system_parameters = c.fetchall()
    current_status = {}
    if system_parameters is not None:
        current_status['race_owner'] = system_parameters[2][1]
        current_status['race_status'] = system_parameters[3][1]
        current_status['lap_threshold'] = system_parameters[0][1]
        current_status['next_race_number'] = int(system_parameters[1][1])
        current_status['current_race_number'] = current_status['next_race_number'] - 1
    return current_status 

def update_system_parameters(race_number, race_status, user_id):
    db, c = get_db()
    c.execute(
        'update system_parameters set value = %s where id = %s', (race_number, 'next_race_number')
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
    race_info['id'] = str(race_number)
    if race is not None:
        race_info['creator'] = race[1]
        if race[2] == 'configure_race':
            race_info['status'] = 'configuring'
        elif race[2] == 'racing':
            race_info['status'] = 'started'
        else:
            race_info['status'] = 'finished'
        race_info['track'] = race[3]
        race_info['category'] = race[4]
        if race_info['category'] == 'Laps race':
            race_info['expectedLaps'] = race[5]
        elif race_info['category'] == 'Time race':
            race_info['expectedTime'] = race[5]   
        if  race_info['status'] == 'finished':
            if race[7] is not None and race[6] is not None:
                race_info['total_time'] = (race[7] - race[6]).seconds
            else:
                race_info['total_time'] = 0
        if race_info['status'] == 'started' or race_info['status'] == 'finished':
            if race[7] is not None and race[6] is not None:
                race_info['total_time'] = (datetime.now()-race[6]).seconds
            else:
                race_info['total_time'] = 0
            if race_info['category'] == 'Time race':
                if race_info['total_time'] > race_info['expectedTime']:
                    race_info['total_time'] = race_info['expectedTime']
                    requests.post("http://localhost:8080/race", json={'stop_race': True, 'user_id': race_info['creator']}).json()
            race_info['date'] = race[6]
        else:
            race_info['total_time'] = 0
        race_info['participants'] = []
        c.execute('select user_id, participant_id from race_competitors where race_number = %s', (race_number, ))
        race_competitors = c.fetchall()
        for competitor in race_competitors:
            race_info['participants'].append(get_competitor_info(race_number=race_number, user_id=competitor[0], requester = user_id, participant_id = competitor[1]))
        if race_info['category'] == 'Laps race' and race_info['status'] == 'started':
            c.execute('select count(lap) from race_competitors_laps where race_number = %s', (race_number, ))
            min_lap = c.fetchone()
            if min_lap is not None:
                if min_lap[0] == race_info['expectedLaps']*len(race_info['participants']):
                    requests.post("http://localhost:8080/race", json={'stop_race': True, 'user_id': race_info['creator']})
        race_info['participants_amount'] = len(race_info['participants'])
    return race_info

def get_competitor_info(race_number, user_id, requester, participant_id):
    db, c = get_db()
    c.execute('select * from race_competitors where race_number = %s and participant_id = %s', (race_number, participant_id))
    competitor = c.fetchone()
    competitor_info = {}
    #competitor_info['race_number'] = race_number
    competitor_info['user'] = user_id
    if competitor is not None:
        competitor_info['toyTag'] = competitor[1]
        competitor_info['nickname'] = competitor[2]
        competitor_info['participant_id'] = competitor[9]
        competitor_info['toy'] = competitor[4]
        competitor_info['rank'] = -1
        competitor_info['guest'] = not competitor[8]
        #competitor_info['gender'] = competitor[5]
        #competitor_info['weight_category'] = competitor[6]
        #competitor_info['photo'] = competitor[7]
        if competitor[7]:
            competitor_info['profilePictureURL'] = url_for('profile_picture', race_number=race_number, participant_id=competitor_info['participant_id'])
        #competitor_info['video_permission'] = competitor[8]
        temp = get_laps_info(race_number, competitor_info['toyTag'], competitor[8] if requester == user_id else False , user_id, competitor_info['participant_id'])
        competitor_info['laps'] = temp['laps']
        
        c.execute(
            'select race_competitors_laps.tag, min(time_milliseconds) from race_competitors_laps INNER JOIN race_competitors ON race_competitors_laps.tag = race_competitors.tag where race_competitors_laps.race_number = %s group by race_competitors_laps.tag order by min(time_milliseconds)',
            (race_number, )
        )
        competitors_rank = c.fetchall()
        rank = 1
        for competitor_rank in competitors_rank:
            if competitor_rank[0] == competitor_info['toyTag']:
                competitor_info['rank'] = rank
            else:
                rank = rank + 1
        competitor_info['bestLap'] = temp['best_time']

    return competitor_info

def get_laps_info(race_number, tag, video_permission, user_id, participant_id):
    db, c = get_db()
    c.execute('select * from race_competitors_laps where race_number = %s and tag = %s', (race_number, tag))
    competitor_laps = c.fetchall()
    competitor_laps_info = {}
    #competitor_laps_info['race_number'] = race_number
    #competitor_laps_info['tag'] = tag
    #competitor_laps_info['video_permission'] = video_permission
    #competitor_laps_info['best_lap'] = -1
    competitor_laps_info['best_time'] = -1
    #competitor_laps_info['laps_amount'] = 0
    competitor_laps_info['laps'] = []
    if competitor_laps is not None:
        #competitor_laps_info['laps_amount'] = len(competitor_laps)
        for competitor_lap in competitor_laps:
            lap = {}
            lap['id'] = str(participant_id) + '_' + str(competitor_lap[2])
            lap['lapNumber'] = competitor_lap[2]
            lap['time'] = competitor_lap[3]/1000
            if lap['time'] < competitor_laps_info['best_time'] or competitor_laps_info['best_time'] == -1:
                competitor_laps_info['best_time'] = lap['time']
                #competitor_laps_info['best_lap'] =  lap['lap']
            if video_permission and competitor_lap[7]:
                #lap['video_name'] = competitor_lap[4]
                lap['videoLink'] = url_for('video', race_number=race_number, tag=tag, lap=competitor_lap[2], user_id=user_id)
            #lap['info_uploaded'] = competitor_lap[5]
            #lap['video_uploaded'] = competitor_lap[6]
            competitor_laps_info['laps'].append(lap)
    return competitor_laps_info

def get_video_info(race_number, tag, lap, user_id):
    db, c = get_db()
    c.execute('select * from race_competitors_laps where race_number = %s and tag = %s and lap = %s', (race_number, tag, lap))
    lap = c.fetchone()
    c.execute('select * from race_competitors where race_number = %s and tag = %s', (race_number, tag))
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
        lap_info['video_available'] = lap[7]
        lap_info['info_uploaded'] = lap[5]
        lap_info['video_uploaded'] = lap[6] 
    return lap_info

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in picture_extensions

@app.route('/status', methods=['GET'])
def status():
    return get_current_status()

@app.route('/system_parameters', methods=['GET'])
def system_parameters():
    return get_system_parameters()

@app.route('/reset_system_parameters', methods=['GET'])
def reset_system_parameters():
    status = get_system_parameters()
    update_system_parameters(race_number=status['next_race_number'], race_status='no race', user_id=' ')
    return get_system_parameters()

@app.route('/race', methods=['POST', 'PUT'])
def race():
    status = get_system_parameters()
    db, c = get_db()
    if status['race_status'] == 'no race' and 'user_id' in request.json and 'create_race' in request.json:
        try:
            user_id = request.json['user_id']
            #race_code = ''.join(random.choice(string.ascii_uppercase) for x in range(4)) 
            race_number = status['next_race_number']
            race_status = 'configure_race'  
            c.execute(
                'insert into races (race_number, user_id, race_status) values (%s, %s, %s)', (race_number , user_id, race_status)
			)
            update_system_parameters(race_number=race_number+1, race_status=race_status, user_id=user_id)
            db.commit()
            return {'ok': True, 'process': 'Start race', 'status': 'success', 'race_number': race_number}
        except Exception as e: 
            return {'ok': False, "error": str(e)} 
    elif status['race_status'] == 'configure_race' and 'user_id' in request.json:
        if status['race_owner'] == request.json['user_id']:
            if 'track' in request.json:
                c.execute(
                    'update races set track = %s where race_number = %s', (request.json['track'], status['current_race_number'])
                )
                db.commit()
                return {'ok': True, 'process': 'Select track', 'status': 'success'} 
            elif 'race_type' in request.json and 'limit_number' in request.json:
                c.execute(
                    'update races set race_type = %s, limit_number = %s where race_number = %s', (request.json['race_type'], request.json['limit_number'], status['current_race_number'])
                )
                db.commit()
                return {'ok': True, 'process': 'Race type', 'status': 'success'}
            elif 'start_race' in request.json:
                try:
                    c.execute(
                        'update races set race_begin_time = %s, race_status = %s where race_number = %s', (datetime.now(), 'racing', status['current_race_number'],)
                    )
                    db.commit()
                    update_system_parameters(race_number=status['next_race_number'], race_status='racing', user_id=status['race_owner'])
                    return {'ok': True, 'process': 'Start Race', 'status': 'success'}
                except Exception as e: 
                    return {'ok': False, "error": str(e)}  
    elif status['race_status'] == 'racing' and 'user_id' in request.json and 'stop_race' in request.json:
        if status['race_owner'] == request.json['user_id'] and request.json['stop_race']:
            try:
                c.execute(
                    'select race_type, limit_number, race_begin_time from races where race_number = %s', (status['current_race_number'], ) 
                )
                race = c.fetchone()
                race_type = race[0]
                race_limit = race[1]
                race_begin_time = race[2]
                finish_time = datetime.now()
                if race_type == 'Time race' and race_limit < (finish_time - race_begin_time).seconds:
                    finish_time = race_begin_time + timedelta(seconds=race_limit)
                c.execute(
                    'update races set race_final_time = %s, race_status = %s where race_number = %s', (finish_time, 'finished', status['current_race_number'],)
                )
                db.commit()
                update_system_parameters(race_number=status['next_race_number'], race_status='no race', user_id=' ')
                return {'ok': True, 'process': 'Stop Race', 'status': 'success'}
            except Exception as e: 
                return {'ok': False, "error": str(e)}       
    return {'ok': False}

@app.route('/race', methods=['GET'])
def race_get():
    status = get_system_parameters()
    if 'user' in request.headers:
        return get_race_info(race_number=status['current_race_number'], user_id=request.headers['user'])
    return {'ok': False} 

@app.route('/create_race', methods=['POST'])
def create_race():
    status = get_system_parameters()
    try:
        if status['race_status'] == 'no race':
            user_id = request.json['user_id']
            #race_code = ''.join(random.choice(string.ascii_uppercase) for x in range(4))
            race_number = status['next_race_number']
            race_status = 'configure_race'
            db, c = get_db()
            c.execute(
                'insert into races (race_number, user_id, race_status) values (%s, %s, %s)', (race_number , user_id, race_status)
			)
            update_system_parameters(race_number=race_number+1, race_status=race_status, user_id=user_id)
            db.commit()
            return {'ok': True, 'process': 'Start race', 'status': 'success', 'race_number': race_number}
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
    except Exception as e: 
        return {'ok': False, "error": str(e)}     
    
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
    except Exception as e: 
        return {'ok': False, "error": str(e)}     
    
@app.route('/participant', methods=['POST'])
def participant():
    status = get_system_parameters()
    try:
        if status['race_status'] == 'configure_race':
            user_id = request.json['user_id']
            nickname = request.json['nickname']
            gender = request.json['gender']
            weight_category = request.json['weight_category']
            toy = request.json['toy']
            tag = request.json['tag']
            if 'guest' in request.json:    
                video_permission = False if request.json['guest'] == True else True
            else:
                video_permission = False
            participant_id = uuid.uuid4()
            db, c = get_db()
            c.execute('select * from race_competitors where race_number = %s and tag = %s',(status['current_race_number'], tag))
            competitor_by_tag = c.fetchone()
            if competitor_by_tag is not None:
                return {'ok': False, 'status': 'failed', 'process': 'Participant', 'error': 'Tag is already used by another participant'}
            if competitor_by_tag is None:
                c.execute(
					'insert into race_competitors (race_number, tag, nickname, user_id, toy, gender, weight_category, video_permission, participant_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
					(status['current_race_number'], tag, nickname, user_id, toy, gender, weight_category, video_permission, str(participant_id))
				)
                db.commit()
                return {'ok': True, 'status': 'success', 'process': 'Participant', 'participant': {
                    'participant_id': participant_id,
                    'nickname': nickname,
                    'user': user_id,
                    'profilePictureURL': None,
                    'toy': toy,
                    'toyTag': tag,
                    'guest': not video_permission}}
            else:
                return {'ok': False, 'status': 'failed', 'process': 'Participant', 'error': 'An error ocurred'}
        else:
            return {'ok': False, 'process': 'Participant', 'status': 'failed'}
    except Exception as e: 
        return {'ok': False, "error": str(e)}     

@app.route('/participant/<participant_id>', methods=['PUT'])
def participant_put(participant_id):
    status = get_system_parameters()
    db, c = get_db()
    c.execute('select * from race_competitors where race_number = %s and participant_id = %s',(status['current_race_number'], participant_id))
    competitor_by_user = c.fetchone()
    if competitor_by_user is not None:
        nickname = request.json['nickname']
        toy = request.json['toy']
        tag = request.json['tag']
        photo = request.json['photo']
        c.execute(
            'update race_competitors set nickname = %s, toy = %s, tag = %s where race_number = %s and participant_id = %s', 
            (nickname, toy, tag, status['current_race_number'], participant_id)
        )
        db.commit()
        return {'ok': True, 'status': 'success', 'process': 'Participant', 'participant': {
                    'participant_id': participant_id,
                    'nickname': nickname,
                    'toy': toy,
                    'toyTag': tag}}
    else:
        return {'ok': False, 'status': 'failed', 'process': 'Participant', 'error': 'User is not registered in the race'}
    
@app.route('/participant_photo/<participant_id>', methods=['POST'])
def participant_photo(participant_id):
    db, c = get_db()
    status = get_system_parameters()
    c.execute('select photo from race_competitors where race_number = %s and participant_id = %s',(status['current_race_number'], participant_id))
    participant_photo = c.fetchone()
    if participant_photo is None:
        return {'ok': False, 'status': 'failed', 'process': 'Participant Photo', 'error': 'User is not registered in the race'}
    if participant_photo[0] == True:
        return {'ok': False, 'status': 'failed', 'process': 'Participant Photo', 'error': 'User already has a photo in the race'}
    try:
        if status['race_status'] == 'configure_race':
            if 'image' not in request.files:
                return {'ok': False, 'error': 'Wrong file type'}
            image = request.files['image']
            if image.filename == '':
                return {'ok': False, 'error': 'Empty file'}
            if image and allowed_file(image.filename):
                try:
                    extension = image.filename.rsplit('.', 1)[1].lower()
                    image.save(str(Path().absolute())+'/static/profile_pictures/'+str(status['current_race_number'])+'_'+str(participant_id)+'.'+extension)
                    c.execute(
                        'update race_competitors set photo = %s where race_number = %s and participant_id = %s', 
                        (True, status['current_race_number'], participant_id)
                    )
                    db.commit()
                    return {'ok': True, 'process': 'Participant Photo', 'participant_id': participant_id, 'photo_url': url_for('profile_picture', race_number=status['current_race_number'], participant_id=participant_id)}
                except Exception as e:
                    return {'ok': False, 'error': 'The file could not be saved due to the following error: '+str(e)}
    except Exception as e: 
        return {'ok': False, "error": str(e)}     

@app.route('/participant_photo/<participant_id>', methods=['PUT'])
def participant_photo_put(participant_id):
    db, c = get_db()
    status = get_system_parameters()
    c.execute('select photo from race_competitors where race_number = %s and participant_id = %s',(status['current_race_number'], participant_id))
    participant_photo = c.fetchone()
    if participant_photo is None:
        return {'ok': False, 'status': 'failed', 'process': 'Participant Photo', 'error': 'User is not registered in the race'}
    if participant_photo[0] == False:
        return {'ok': False, 'status': 'failed', 'process': 'Participant Photo', 'error': 'User does not has a photo in the race'}
    try:
        if status['race_status'] == 'configure_race':
            if 'image' not in request.files:
                return {'ok': False, 'error': 'Wrong file type'}
            image = request.files['image']
            if image.filename == '':
                return {'ok': False, 'error': 'Empty file'}
            if image and allowed_file(image.filename):
                try:
                    extension = image.filename.rsplit('.', 1)[1].lower()
                    image.save(str(Path().absolute())+'/static/profile_pictures/'+str(status['current_race_number'])+'_'+str(participant_id)+'.'+extension)
                    c.execute(
                        'update race_competitors set photo = %s where race_number = %s and participant_id = %s', 
                        (True, status['current_race_number'], participant_id)
                    )
                    db.commit()
                    return {'ok': True, 'process': 'Participant Photo', 'participant_id': participant_id, 'photo_url': url_for('profile_picture', race_number=status['current_race_number'], participant_id=participant_id)}
                except Exception as e:
                    return {'ok': False, 'error': 'The file could not be saved due to the following error: '+str(e)}
    except Exception as e: 
        return {'ok': False, "error": str(e)}  
    
@app.route('/participant_photo/<participant_id>', methods=['DELETE'])
def participant_photo_delete(participant_id):
    db, c = get_db()
    status = get_system_parameters()
    c.execute('select photo from race_competitors where race_number = %s and participant_id = %s',(status['current_race_number'], participant_id))
    participant_photo = c.fetchone()
    if participant_photo is None:
        return {'ok': False, 'status': 'failed', 'process': 'Participant Photo', 'error': 'User is not registered in the race'}
    if participant_photo[0] == False:
        return {'ok': False, 'status': 'failed', 'process': 'Participant Photo', 'error': 'User does not has a photo in the race'}
    try:
        if status['race_status'] == 'configure_race':
            path = '/home/Trelainn/Documents/TimerTesting/static/profile_pictures/'
            name = str(status['current_race_number']) + '_' + str(participant_id)
            files = []
            for file in os.listdir(path):
                files.append(file)
                if file.startswith(name):
                    image = os.path.join(path, file)
                    os.remove(image)
                    c.execute(
                        'update race_competitors set photo = %s where race_number = %s and participant_id = %s', 
                        (False, status['current_race_number'], participant_id)
                    )
                    db.commit()
                    return {'ok': True, 'process': 'Participant Photo', 'participant_id': participant_id, 'photo_url': None}
            return {'ok': False}
    except Exception as e: 
        return {'ok': False, "error": str(e)}  

@app.route('/start_race', methods=['POST'])
def start_race():
    status = get_system_parameters()
    user_id = request.json['user_id']
    try:
        if status['race_status'] == 'configure_race' and status['race_owner'] == user_id:
            db, c = get_db()
            c.execute(
                'update races set race_begin_time = %s, race_status = %s where race_number = %s', (datetime.now(), 'racing', status['current_race_number'],)
			)
            db.commit()
            update_system_parameters(race_number=status['next_race_number'], race_status='racing', user_id=status['race_owner'])
            return {'ok': True, 'process': 'Start Race', 'status': 'success'}
        return {'ok': False, 'process': 'Start Race', 'status': 'failed'}
    except Exception as e: 
        return {'ok': False, "error": str(e)}     

@app.route('/record_time', methods=['POST'])
def record_time():
    tag = request.json['tag']
    time = request.json['time']
    status = get_system_parameters()
    try:
        if status['race_status'] == 'racing':
            db, c = get_db()
            c.execute('select video_permission, user_id from race_competitors where tag = %s and race_number = %s', (tag, status['current_race_number']))
            participant = c.fetchall()
            if participant != []:
                video_permission = participant[0][0]
                user_id = participant[0][0]
            else:
                return {'ok': False, "error": "tag not registered in race"} 
            c.execute('select lap from race_competitors_laps where tag = %s and race_number = %s order by lap desc', (tag, status['current_race_number']))
            lap_number = c.fetchone()
            race = get_race_info(status['current_race_number'], user_id)
            if lap_number is not None:
                lap_number = int(lap_number[0])+ 1
            else:
                lap_number = 1
            if video_permission:
                video_name = str(status['current_race_number'])+'_'+str(tag)+'_'+str(lap_number)
            else:
                video_name = ''
            if race['category'] == 'Laps race':
                if lap_number <= race['expectedLaps']:
                    c.execute('insert into race_competitors_laps (race_number, tag, lap, time_milliseconds) values (%s, %s, %s, %s)', (status['current_race_number'], tag, lap_number, time))
                    db.commit()
                    return {'ok': True, 'process': 'Record Time', 'status': 'success', 'race_number': status['current_race_number'], 'tag': tag, 'lap_number': lap_number, 'time':time, 'video_name': video_name, 'video_permission': video_permission}
            elif race['category'] == 'Time race':
                if race['total_time'] <= race['expectedTime']:
                    c.execute('insert into race_competitors_laps (race_number, tag, lap, time_milliseconds) values (%s, %s, %s, %s)', (status['current_race_number'], tag, lap_number, time))
                    db.commit()
                return {'ok': True, 'process': 'Record Time', 'status': 'success', 'race_number': status['current_race_number'], 'tag': tag, 'lap_number': lap_number, 'time':time, 'video_name': video_name, 'video_permission': video_permission}
            return {'ok': False, 'process': 'Record Time', 'status': 'failed', 'error': 'Out of limits'}
        return {'ok': False, 'process': 'Record Time', 'status': 'failed'}
    except Exception as e: 
        return {'ok': False, "error": str(e), "participant": participant}     

@app.route('/saved_video', methods=['POST'])
def saved_video():
    tag = str(request.json['tag'])
    race_number = int(request.json['race_number'])
    lap_number = int(request.json['lap_number'])
    try:
        db, c = get_db()
        c.execute('update race_competitors_laps set video_available = %s where tag = %s and race_number = %s and lap = %s', (True, tag, race_number, lap_number))
        db.commit()
        return {'ok': True, 'process': 'Video Saved', 'status': 'success', 'race_number': race_number, 'tag': tag, 'lap_number': lap_number}
    except Exception as e: 
        return {'ok': False, "error": str(e)}     

@app.route('/stop_race', methods=['POST'])
def stop_race():
    status = get_system_parameters()
    user_id = request.json['user_id']
    try:
        if status['race_status'] == 'racing' and status['race_owner'] == user_id:
            db, c = get_db()
            c.execute(
                'update races set race_final_time = %s, race_status = %s where race_number = %s', (datetime.now(), 'finished', status['current_race_number'],)
			)
            db.commit()
            update_system_parameters(race_number=status['next_race_number'], race_status='no race', user_id=' ')
            return {'ok': True, 'process': 'Stop Race', 'status': 'success'}
        return {'ok': False, 'process': 'Stop Race', 'status': 'failed'}
    except Exception as e: 
        return {'ok': False, "error": str(e)}     

@app.route('/view_race', methods=['GET'])
def view_race():
    user_id = request.json['user_id']
    race_number = request.json['race_number']
    system_parameters = get_system_parameters()
    return get_race_info(race_number=race_number, user_id=user_id)
    if system_parameters['race_number']-1 == race_number:
        return get_race_info(race_number=race_number, user_id=user_id)
    else:
        pass

@app.route('/view_participants', methods=['GET'])
def view_participants():
    db, c = get_db()
    status = get_system_parameters()
    try:
        if status['race_status'] == 'racing':
            c.execute('select tag from race_competitors where race_number = %s', (status['current_race_number'], ))
            race_competitors = c.fetchall()
            participants = []
            for competitor in race_competitors:
                participants.append(competitor[0])
    except:
        pass
    return participants

@app.route('/video/<race_number>/<tag>/<lap>/<user_id>', methods=['GET'])
def video(race_number, tag, lap, user_id):
    try:
        video_info = get_video_info(race_number=race_number, tag=tag, lap=lap, user_id=user_id)
        if video_info['video_available']:
            return send_file('/home/Trelainn/Documents/TimerTesting/static/videos/'+str(race_number)+'_'+str(tag)+'_'+str(lap)+'.mp4', as_attachment=True)
        else:
            if video_info['video_uploaded']:
                return Response("Server available", status=400,)
            return Response("No video available", status=403,)
    except Exception as e:
        return {'ok': False, "error": str(e)} 
    
@app.route('/profile_picture/<race_number>/<participant_id>', methods=['GET'])
def profile_picture(race_number, participant_id):
    path = '/home/Trelainn/Documents/TimerTesting/static/profile_pictures/'
    name = str(race_number) + '_' + str(participant_id)
    files = []
    for file in os.listdir(path):
        files.append(file)
        if file.startswith(name):
            image = os.path.join(path, file)
            extension = image.rsplit('.', 1)[1].lower()
            return send_file(image, as_attachment=True, download_name=str(race_number)+'.'+extension)
    return {'ok': False}

@app.route('/update_status', methods=['POST'])
def update_status():
    db, c = get_db()
    status = get_system_parameters()
    res = request.json
    temperature = request.json['Temperature']
    battery_percentage = round(request.json['Voltage_C1'] + request.json['Voltage_C2'] + request.json['Voltage_C3'] + request.json['Voltage_C4'], 2)
    pcb_connection = request.json['Raspberry_Connected']
    starting_system = request.json['Starting_System']
    system_shut_down = request.json['System_Shut_Down']
    charger_connected = request.json['Charging']
    camera_on = request.json['Camera_On']
    antenna_on = request.json['Antenna_On']
    internet_available = request.json['Internet_Available']
    led_status = request.json['LED_Status']
    c.execute(
        'insert into system_tracker (date, battery_percentage, temperature, race_status, race_number, camera_on, antenna_on, pcb_connection, internet_available, led_status, charger_connected, starting_system, system_shut_down) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
        (datetime.now(),battery_percentage, temperature, status['race_status'][0:9], status['next_race_number'], camera_on, antenna_on, pcb_connection, internet_available, led_status[0:9], charger_connected, starting_system, system_shut_down)
    )
    db.commit()
    return {'ok': True} 

@app.route('/update_lap_threshold', methods=['POST'])
def update_lap_threshold():
    db, c = get_db()
    lap_threshold = request.json['lap_threshold']
    c.execute(
        'update system_parameters set value = %s where id = %s', (lap_threshold, 'lap_threshold')
    )
    db.commit()
    return {'ok': True} 

@app.route('/update_list_wifi_networks', methods=['POST'])
def update_list_wifi_networks():
    global wifi_list
    wifi_list = request.json
    return {'ok': True} 

@app.route('/list_wifi_networks', methods=['GET'])
def list_wifi_networks():
    return wifi_list

@app.route('/connect_wifi_network', methods=['POST'])
def connect_wifi_network():
    global wifi_network_change_data
    wifi_network_change_data = {'change': True, 'SSID': request.json['SSID'], 'Password': request.json['Password'], 'Hotspot': False}
    return {'ok:': True}

@app.route('/create_hotspot', methods=['POST'])
def create_hotspot():
    global wifi_network_change_data
    wifi_network_change_data = {'change': True, 'SSID': request.json['SSID'], 'Password': request.json['Password'], 'Hotspot': True}
    return {'ok:': True}

@app.route('/update_wifi_network', methods=['GET'])
def update_wifi_network():
    global wifi_network_change_data
    temp = wifi_network_change_data
    wifi_network_change_data = {'change': False}
    return temp

@app.route('/close_past_races', methods=['POST'])
def close_past_races():
    status = get_system_parameters()
    db, c = get_db()
    try:
        c.execute(
            'update races set race_status = %s where race_status <> %s', ('finished', 'finished')
        )
        db.commit()
        update_system_parameters(race_number=status['next_race_number'], race_status='no race', user_id=' ')
        return {'ok': True}
    except Exception as e:
        return {'ok': False, "error": str(e)}   

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