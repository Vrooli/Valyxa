import os
import redis
from time import sleep
from dotenv import load_dotenv

load_dotenv()

def main():
    redis_url = os.environ["REDIS_URL"]
    r = redis.Redis.from_url(redis_url)

    key = "test_key"
    value = "Hello, Redis!"

    r.set(key, value)
    print(f"Set key-value pair: {key} - {value}")

    sleep(1)

    retrieved_value = r.get(key).decode('utf-8')
    print(f"Retrieved value for key '{key}': {retrieved_value}")

if __name__ == "__main__":
    main()
