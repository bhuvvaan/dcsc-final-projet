#!/usr/bin/env python3

from flask import Flask, request, Response
import jsonpickle
import os
import logging
from PIL import Image
import base64
import io
import numpy as np
import json
import hashlib
import redis
import json
from minio import Minio
import base64
import io

# Initialize the Flask application
app = Flask(__name__)

# Initialize logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)

# Configure log format and handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
log.addHandler(console_handler)

REDIS_MASTER_SERVICE_HOST = os.environ.get('REDIS_MASTER_SERVICE_HOST') or 'localhost'
REDIS_MASTER_SERVICE_PORT = os.environ.get('REDIS_MASTER_SERVICE_PORT') or 6379

@app.route('/apiv1/separate', methods=['POST'])
def separate():
    full_mp3 = request.get_json()

    # Serialize the JSON data to a string
    json_string = json.dumps(full_mp3['mp3'], sort_keys=True)
    
    # Hash the serialized JSON string using SHA-256
    hash_object = hashlib.sha256(json_string.encode())
    hex_hash = hash_object.hexdigest()

    response = {
        'hash': hex_hash,
        'reason': "Song enqueued for separation"
    }
    
    # Encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)
    
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

    # Read the task from the queue
    # We'll read from the 'toWorker' queue as an example
    task_from_queue = redis_client.lpop("toWorker")  # Using lpop to read and remove the first element
    if task_from_queue:
        task_data = jsonpickle.decode(task_from_queue)  # Decode the pickled data
        app.logger.debug(f"Task read from Redis: {task_data}")
    else:
        app.logger.debug("No task found in the Redis queue.")

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
    except Exception as err:
        app.logger.error("Error uploading the MP3 file")
        app.logger.error(str(err))

    return Response(response=response_pickled, status=200, mimetype="application/json")

# Start Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9999, debug=True)
