import uuid
import datetime
from common.database import Database
from models.asset import Asset

__author__ = 'jslvtr'


class Portfolio(object):
    def __init__(self, asset_name, asset_weight, starting_time, ending_time, _id=None):
        self.asset_name = asset_name
        self.asset_weight = asset_weight
        self.starting_time = starting_time
        self.ending_time= ending_time
        self._id = uuid.uuid4().hex if _id is None else _id

    
    def new_asset(self, asset_name, asset_weight):#, date=datetime.datetime.utcnow()):
        asset = Asset(portfolio_id=self._id,
                    asset_name=asset_name,
                    asset_weight=asset_weight)
        asset.save_to_mongo()
    

    def get_asset(self):
        return Asset.from_portfolio(self._id)

    def save_to_mongo(self):
        Database.insert(collection='portfolio',
                        data=self.json())

    def json(self):
        return {
            '_id': self._id,
            'asset_name': self.asset_name,
            'asset_weight': self.asset_weight,
            'starting_time': self.starting_time,
            'ending_time': self.ending_time
        }

    @classmethod
    def from_mongo(cls, id):
        portfolio_data = Database.find_one(collection='asset',
                                      query={'_id': id})
        return cls(**portfolio_data)

    @classmethod
    def find_by_author_id(cls, author_id):
        portfolio = Database.find(collection='asset',
                              query={'author_id': author_id})
        return [cls(**portfolio) for portfolio in portfolios]
