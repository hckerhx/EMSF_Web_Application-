import datetime
import uuid
from flask import session
from common.database import Database
from models.portfolio import Portfolio

__author__ = 'hckerhx'

class User(object):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    # filter through user by their email
    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("users", {"email": email})
        if data is not None:
            return cls(**data)

    # filter through user by their ID 
    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)
 
    @staticmethod
    def login_valid(email, password):
        # Check whether a user's email matches the password they sent us
        user = User.get_by_email(email)
        if user is not None:
            # Check the password
            return user.password == password 
        return False

    @classmethod
    def register(cls, email, password): # hash password
        user = cls.get_by_email(email)
        if user is None:
            # User doesn't exist, so we can create it
            new_user = cls(email, password)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        else:
            # User exists :(
            return False

    @staticmethod
    def login(user_email):
        # login_valid has already been called
        session['email'] = user_email

    @staticmethod
    def logout():
        session['email'] = None

    # get portfolio/return the portfolio that belongs to the user
    def get_portfolio(self):
        return Portfolio.find_by_author_id(self._id)

    # create new blog under the user accounts 
    def new_portfolio(self, starting_time, ending_time):
        portfolio = Portfolio(author=self.email,
                    starting_time=starting_time,
                    ending_time=ending_time,
                    author_id=self._id)

        portfolio.save_to_mongo()

    @staticmethod
    def new_asset(portfolio_id, asset_name, asset_weight):#, date=datetime.datetime.utcnow()):
        portfolio = Portfolio.from_mongo(portfolio_id)
        portfolio.new_asset(asset_name=asset_name,
                      asset_weight=asset_weight)

    # user account format 
    def json(self):
        return {
            "email": self.email,
            "_id": self._id,
            "password": self.password
        }

    def save_to_mongo(self):
        Database.insert("users", self.json())
