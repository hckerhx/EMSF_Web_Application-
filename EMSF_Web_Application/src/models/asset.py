import uuid
from common.database import Database
import datetime

__author__ = 'jslvtr'


class Asset(object):

    def __init__(self, portfolio_id, asset_name, asset_weight, _id=None): #created_date=datetime.datetime.utcnow(), 
        self.portfolio_id = portfolio_id
        self.asset_name = asset_name
        self.asset_weight = asset_weight
        #self.author = author
        #self.created_date = created_date
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='asset',
                        data=self.json())

    def json(self):
        return {
            '_id': self._id,
            'portfolio_id': self.portfolio_id,
            'asset_name': self.asset_name,
            'asset_weight': self.asset_weight,
            #'title': self.title,
            #'created_date': self.created_date
        }

    @classmethod
    def from_mongo(cls, id):
        asset_data = Database.find_one(collection='asset', query={'_id': id})
        return cls(**asset_data)

    @staticmethod
    def from_portfolio(id):
        return [asset for asset in Database.find(collection='asset', query={'portfolio_id': id})]