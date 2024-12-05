#!/usr/bin/env python3

import os
import logging
import hashlib
import base64
import io
import sqlite3
from flask import Flask, request, Response, session, redirect, url_for, flash, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from minio import Minio
from flask_cors import CORS
from flask import redirect
import jsonpickle
from PIL import Image
import numpy as np
import redis
import json



# Initialize the Flask application
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB
CORS(app, resources={r"/apiv1/*": {"origins": "*"}})

# Logging setup
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
log.addHandler(console_handler)

REDIS_MASTER_SERVICE_HOST = os.environ.get('REDIS_MASTER_SERVICE_HOST') or 'localhost'
REDIS_MASTER_SERVICE_PORT = os.environ.get('REDIS_MASTER_SERVICE_PORT') or 6379

# Initialize SQLite database for users
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Decorator for authentication
def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_view

@app.route('/')
def home():
    return redirect('/register')  # Redirect to the login page

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO user (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Username already exists!')
            return redirect(url_for('register'))
        conn.close()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):  # user[2] is the hashed password
            session['user_id'] = user[0]  # user[0] is the user ID
            flash('Login successful!')
            return redirect(url_for('upload'))
        else:
            flash('Invalid username or password!')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/upload')
@login_required
def upload():
    return render_template('upload.html')

@app.route('/apiv1/separate', methods=['POST'])
@login_required
def separate():
    full_mp3 = request.get_json()

    # Serialize the JSON data to a string
    json_string = json.dumps(full_mp3['mp3'], sort_keys=True)
    
    # Hash the serialized JSON string using SHA-256
    hash_object = hashlib.sha256(json_string.encode())
    hex_hash = hash_object.hexdigest()

    response = {
        'hash': hex_hash,
        'reason': "Song enqueued for separation",
        'name': full_mp3['callback']['data']['mp3']
    }

    response_to_frontend = {
        'output': "File enqueued for processing, please await download link!"
    }
    
    # Encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    # Encode response using jsonpickle
    response_frontend_pickled = jsonpickle.encode(response_to_frontend)

    # Read the task from the queue  
    # We'll read from the 'toWorker' queue as an example
    # task_from_queue = redis_client.lpop("toWorker")  # Using lpop to read and remove the first element
    # if task_from_queue:
    #     task_data = jsonpickle.decode(task_from_queue)  # Decode the pickled data
    #     app.logger.debug(f"Task read from Redis: {task_data}")
    # else:
    #     app.logger.debug("No task found in the Redis queue.")

    #######################################################################################################
    # MINIO
    minioHost = os.getenv("MINIO_HOST") or "minio:9000"
    minioUser = os.getenv("MINIO_USER") or "rootuser"
    minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"

    client = Minio(minioHost,
                   secure=False,
                   access_key=minioUser,
                   secret_key=minioPasswd)

    bucketname = 'demucs-bucket'

    # Assuming your MP3 data is stored in a JSON object like this
    encoded_mp3_json = {
        'mp3': full_mp3['mp3']  
    }

    # Decode the base64-encoded mp3 data
    decoded_mp3_data = base64.b64decode(encoded_mp3_json['mp3'])

    # Create a file-like object to upload to Minio
    mp3_stream = io.BytesIO(decoded_mp3_data)

    # Define a file name for the MP3 object
    mp3_filename = hex_hash

    # Create bucket if it does not exist
    if not client.bucket_exists(bucketname):
        app.logger.debug(f"Creating bucket: {bucketname}")
        client.make_bucket(bucketname)

    try:
        # Upload the MP3 data to Minio
        app.logger.debug(f"Uploading {mp3_filename} to {bucketname}")
        client.put_object(bucketname, mp3_filename, mp3_stream, len(decoded_mp3_data))
        app.logger.debug(f"Successfully uploaded {mp3_filename} to {bucketname}")
        ###########################################################################################################
        # REDIS
        # Connect to Redis
        redis_client = redis.StrictRedis(host=REDIS_MASTER_SERVICE_HOST, port=int(REDIS_MASTER_SERVICE_PORT), db=0, decode_responses=True)

        # Key for the task queue
        task_queue = "toWorker"
        redis_client.rpush(task_queue, response_pickled)
        app.logger.debug("Task pushed to Redis queue.")

        # Key for the logging queue
        task_queue = "logging"
        redis_client.rpush(task_queue, response_pickled)
        app.logger.debug("Task pushed to Redis logging queue.")
    except Exception as err:
        app.logger.error("Error uploading the MP3 file")
        app.logger.error(str(err))

    return Response(response=response_frontend_pickled, status=200, mimetype="application/json")
# Start Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9999, debug=True)
