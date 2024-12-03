import os
import logging
import sys
import redis
import time

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def main():
    logging.info("Redis Reader Script started")

    # Redis client setup
    REDIS_MASTER_SERVICE_HOST = os.getenv('REDIS_MASTER_SERVICE_HOST', 'redis-master')
    REDIS_MASTER_SERVICE_PORT = int(os.getenv('REDIS_MASTER_SERVICE_PORT', '6379'))

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

    # Main loop to read messages from Redis
    while True:
        try:
            task_from_queue = redis_client.lpop("toWorker")
            if task_from_queue:
                logging.info(f"Received task: {task_from_queue}")
            else:
                logging.info("No tasks in queue, waiting...")
                time.sleep(5)

        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            logging.info("Continuing to next iteration...")
            time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")