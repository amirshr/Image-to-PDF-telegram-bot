import redis
import os
from dotenv import load_dotenv



load_dotenv()

dir_path = os.path.dirname(os.path.realpath(__file__))

r = redis.Redis(host='redis-13116.c11.us-east-1-3.ec2.cloud.redislabs.com', port=13116,
                password='QdG67kPaMaLLJTA41h0NVYdT5tihsmuB')


class Store:
    def __init__(self, user_id):
        self.user_id = user_id

    def store_user(self):
        try:
            r.set(self.user_id, 1)
        except Exception as e:
            print(e)
            pass
