import os
import logging
import sys
import redis
import time
from minio import Minio, S3Error
import subprocess
import jsonpickle
import shutil
import re

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def main():
    logging.info("Script started")

    # Redis client setup
    REDIS_MASTER_SERVICE_HOST = os.getenv('REDIS_MASTER_SERVICE_HOST', 'redis-master')
    REDIS_MASTER_SERVICE_PORT = int(os.getenv('REDIS_MASTER_SERVICE_PORT', '6379'))

    # MinIO client setup
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio:9000')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'rootuser')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'rootpass123')

    # Initialize the Redis client with reconnection logic
    while True:
        try:
            redis_client = redis.StrictRedis(
                host=REDIS_MASTER_SERVICE_HOST,
                port=REDIS_MASTER_SERVICE_PORT,
                db=0,
                decode_responses=True
            )
            redis_client.ping()
            logging.info('Connected to Redis')
            break
        except redis.ConnectionError as e:
            logging.error(f"Redis connection failed: {e}")
            logging.info("Retrying in 5 seconds...")
            time.sleep(5)

    # Test MinIO connection
    try:
        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
        logging.info("Connected to MinIO")
    except S3Error as e:
        logging.error(f"Failed to connect to MinIO: {e}")
        return

    # Main loop to process tasks 
    while True:
        try:
            task_from_queue = redis_client.lpop("toWorker")
            if task_from_queue:
                task_data = jsonpickle.decode(task_from_queue)
                name_of_file = task_data['hash']
                logging.info(f"Type of name_of_file: {type(name_of_file)}")
                logging.info(f"Processing file: {name_of_file}")

                # Directories
                input_dir = 'input'
                output_dir = 'output'

                # Ensure directories exist
                os.makedirs(input_dir, exist_ok=True)
                os.makedirs(output_dir, exist_ok=True)

                # Download the MP4 file from MinIO
                input_file_path = os.path.join(input_dir, f'{name_of_file}.mp4')
                minio_client.fget_object("video-bucket", name_of_file, input_file_path)
                logging.info(f"Downloaded {name_of_file} to {input_file_path}")

                script_path = os.path.abspath("./video_reader.py")
                if not os.path.exists(script_path):
                    logging.error(f"Script not found: {script_path}")
                    sys.exit(1)
                # Command to call your script

                logging.info(f"Input directory: {input_dir}")
                logging.info(f"Output directory: {output_dir}")
                logging.info(f"Input file path: {input_file_path}")
                logging.info(f"Name of file: {name_of_file} (type: {type(name_of_file)})")

                input_file_path = os.path.join(input_dir, f"{name_of_file}.mp4")
                logging.info(f"Constructed input_file_path: {input_file_path}")

                only_integers = "".join(re.findall(r'\d+', name_of_file))[:5]
                brainservice_command = [
                    sys.executable,  # Ensures the script runs with the current Python interpreter
                    script_path,
                    "--video_path", input_file_path,
                    "--output_dir", output_dir,
                    "--interval", str(3),
                    "--id", str(only_integers)
                ]

                logging.info(f"Input file path: {input_file_path}")
                logging.info(f"Command to execute: {' '.join(brainservice_command)}")


                result = subprocess.run(brainservice_command, check=True, capture_output=True, text=True)
                logging.info("Brainservice processing completed successfully.")
                logging.info("Standard Output: %s", result.stdout)
                logging.info("Standard Error: %s", result.stderr)

                # # Create a new bucket for the output files if it doesn't exist
                # results_bucket_name = "ppt-bucket"
                # if not minio_client.bucket_exists(results_bucket_name):
                #     minio_client.make_bucket(results_bucket_name)
                #     logging.info(f"Created new bucket: {results_bucket_name}")

                # # Upload output files to the results bucket with file name as prefix
                # output_subdirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]

                # for subdir in output_subdirs:
                #     subdir_path = os.path.join(output_dir, subdir)
                #     for inner_subdir in os.listdir(subdir_path):
                #         inner_subdir_path = os.path.join(subdir_path, inner_subdir)
                #         if os.path.isdir(inner_subdir_path):
                #             for file in os.listdir(inner_subdir_path):
                #                 file_path = os.path.join(inner_subdir_path, file)
                #                 if os.path.isfile(file_path):
                #                     # Add the file name as a prefix to the object name
                #                     object_name = f"{name_of_file}/{inner_subdir}/{file}"

                #                     # Upload the file to the results bucket
                #                     minio_client.fput_object(
                #                         results_bucket_name,
                #                         object_name,
                #                         file_path
                #                     )
                #                     logging.info(f"Uploaded {object_name} to bucket {results_bucket_name}.")

                response = {
                    'hash': str(name_of_file),
                    'id': str(only_integers)
                }
                response_pickled = jsonpickle.encode(response)
                # pushing task to the task queue
                task_queue = "toRest"
                redis_client.rpush(task_queue, response_pickled)
                logging.info(f'Task processing of {name_of_file} completed and message posted in Redis')

                # Clean up input and output directories after processing
                shutil.rmtree(input_dir)
                shutil.rmtree(output_dir)

            else:
                logging.info("No tasks in queue, waiting...")
                time.sleep(5)

        except S3Error as e:
            logging.error(f"An S3 error occurred: {e}")
        except subprocess.CalledProcessError as e:
            logging.error("An error occurred during Brainservice processing:")
            logging.error("Return Code: %s", e.returncode)
            logging.error("Standard Output: %s", e.stdout)
            logging.error("Error Output: %s", e.stderr)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            logging.info("Continuing to next iteration...")
            time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")