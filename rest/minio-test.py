 #!/usr/bin/env python3
import base64
import io
import logging
import os
import redis
from minio import Minio
import glob
import uuid
import json



minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"
print(f"Getting minio connection now for host {minioHost}!")

MINIO_CLIENT = None
BUCKET_NAME = "user-uploaded-video-bucket"
PPT_BUCKET_NAME = "ppt-result"

FILE_PATH = r"D:\Masters\Fall 2024\data_center_scale_computing\Project\dcsc_final_project\videoplayback.mp4"
FILE_NAME = '999777_video.mp4'

try:
    MINIO_CLIENT = Minio(minioHost, access_key=minioUser, secret_key=minioPasswd, secure=False)
except Exception as exp:
    print(f"Exception raised in worker loop: {str(exp)}")

# if not MINIO_CLIENT.bucket_exists(PPT_BUCKET_NAME):
#     MINIO_CLIENT.make_bucket(PPT_BUCKET_NAME)
#     print(f"Bucket '{PPT_BUCKET_NAME}' created successfully.")
# else:
#     print(f"Bucket '{PPT_BUCKET_NAME}' already exists.")


try:

    # 1. Create a bucket if it doesn't exist
    if not MINIO_CLIENT.bucket_exists(BUCKET_NAME):
        MINIO_CLIENT.make_bucket(BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' created successfully.")
    else:
        print(f"Bucket '{BUCKET_NAME}' already exists.")

    # 2. Upload a file to the bucket
    MINIO_CLIENT.fput_object(
        BUCKET_NAME,
        FILE_NAME,
        FILE_PATH,
    )
    print(f"File '{FILE_PATH}' uploaded to bucket '{BUCKET_NAME}' as '{FILE_NAME}'.")

    # # 3. Access the file (generate a presigned URL)
    # presigned_url = MINIO_CLIENT.presigned_get_object(BUCKET_NAME, FILE_NAME)
    # print(f"Access the file at: {presigned_url}")


except Exception as exp:
    print(f"An error occurred: {exp}")





# @app.route('/apiv1/separate', methods=['POST'])
# def seperate():
#     post_data = json.loads(request.data)
#     mp3_raw = post_data['mp3']
#     mp3_encoded = mp3_raw.encode('utf-8')
#     mp3_bytes = base64.b64decode(mp3_encoded)
#     mp3_data = io.BytesIO(mp3_bytes)
#     mp3_length = len(mp3_bytes)
#     callback = post_data['callback']
#     print("The callback is ", callback)
#     found = MINIO_CLIENT.bucket_exists(BUCKET_NAME)
#     if not found:
#        MINIO_CLIENT.make_bucket(BUCKET_NAME)
#     file_name = str(uuid.uuid4()) + ".mp3"
#     print("Creating filename", file_name)
#     MINIO_CLIENT.put_object(BUCKET_NAME,
#                   file_name,
#                   data=mp3_data,
#                   length=mp3_length)

#     data = {
#         'file_name' : file_name,
#         'context' : callback
#     }
#     print("Pushing to queue", REDIS_KEY,data)
#     count = r.lpush(REDIS_KEY,json.dumps(data))
#     r.lpush("logging", f"Pushed file to queue {file_name}")
#     print("Current queue length", count)
#     response = {
#         "hash": file_name,
#         "reason": "Song enqueued for separation"
#     }
#     response_pickled = jsonpickle.encode(response)
#     return Response(response=response_pickled, status=200, mimetype="application/json")

# @app.route('/apiv1/queue', methods=['GET'])
# def queue():
#     current_files = list(map(str,r.lrange(REDIS_KEY, 0, -1)))
#     response = {'queue' : current_files}
#     response_pickled = jsonpickle.encode(response)
#     return Response(response=response_pickled, status=200, mimetype="application/json")

# @app.route('/apiv1/track', methods=['GET'])
# def get_track():
#     args = request.args.to_dict()
#     file_id = args['file_id']
#     component = args['component'] + ".mp3"
#     MINIO_CLIENT.fget_object(file_id, component, component)
#     return send_file(component,as_attachment=True)

# @app.route('/apiv1/remove', methods=['GET'])
# def remove():
#     args = request.args.to_dict()
#     file_id = args['file_id']
#     found = MINIO_CLIENT.bucket_exists(file_id)
#     if found:
#         files = list(map(lambda x : x.object_name, MINIO_CLIENT.list_objects(file_id)))

#         print("removing files", files, "from bucket", file_id)
#         for file in files:
#             MINIO_CLIENT.remove_object(file_id, file)
#         MINIO_CLIENT.remove_bucket(file_id)
#         response = {'response' : f"Removed bucket {file_id}"}
#         response_pickled = jsonpickle.encode(response)
#         return Response(response=response_pickled, status=200, mimetype="application/json")
#     else:
#         response = {'response' : f"Bucket {file_id} does not exist"}
#         response_pickled = jsonpickle.encode(response)
#         return Response(response=response_pickled, status=200, mimetype="application/json")

# # @app.route('/', methods=['GET'])
# # def hello():
# #     return 'Music Separation Server\n'

# @app.route('/', methods=['GET'])
# def hello():
#     return '\health endpoint Music Separation Server\n'

# app.run(host="0.0.0.0", port=5001)
