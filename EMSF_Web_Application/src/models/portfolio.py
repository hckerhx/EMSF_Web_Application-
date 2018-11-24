import uuid
from common.database import Database
import datetime

__author__ = 'hckerhx'

class portfolio(object):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)


    def json(self):
        return  {
            'asset': self.json
            'weights': self.json
        }




