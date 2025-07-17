from kombu import Connection
from dotenv import load_dotenv
import os

load_dotenv()


def test_connect():
    redis_url = os.getenv("CELERY_BROKER_URL")
    print(f"\nredis_url: {redis_url}")
    try:
        with Connection(redis_url, connect_timeout=1) as conn:
            conn.ensure_connection()
            print("\nSuccessfully connected to Redis.")
    except Exception as e:
        print(f"\nFailed to connect to Redis: {e}")
