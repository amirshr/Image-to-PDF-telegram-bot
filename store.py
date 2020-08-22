import redis
import os
import dropbox
import random
from dotenv import load_dotenv

load_dotenv()

dir_path = os.path.dirname(os.path.realpath(__file__))
access_token = os.getenv('ACCESS_TOKEN')

dbx = dropbox.Dropbox(access_token)

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)


class Store:
    def __init__(self, user_id):
        self.user_id = user_id

    def upload(self):
        for el in os.scandir(dir_path + '/UserData/' + self.user_id):
            if el.name[-3:] == 'pdf':
                with open(el.path, 'rb') as f:
                    dbx.files_upload(f.read(), f'/UserData/{self.user_id}_{random.randint(1, 10000)}.pdf')

    def store_user(self):
        redis.set(self.user_id, 1)
        redis.save()
