import os
import dropbox
from dotenv import load_dotenv

load_dotenv()

dir_path = os.path.dirname(os.path.realpath(__file__))
access_token = os.getenv('ACCESS_TOKEN')

dbx = dropbox.Dropbox(access_token)


class UploadToDrive:
    def __init__(self, user_id):
        self.user_id = user_id

    def upload(self):
        for el in os.scandir(dir_path + '/UserData/' + self.user_id):
            if el.name[-3:] == 'pdf':
                with open(el.path, 'rb') as f:
                    dbx.files_upload(f.read(), f'/UserData/{self.user_id}.pdf')
