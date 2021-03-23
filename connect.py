import os
from pymongo import MongoClient

MONGO_USERNAME = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASS')
MONGO_HOSTLIST = os.getenv('MONGO_HOST')
MONGO_DATABASE = os.getenv('MONGO_DATA')

class Connect(object):
    
    def get_connection(object):
        return MongoClient("mongodb://"+object.username+":"+object.password+"@"+object.hostlist+"/"+object.database+"?retryWrites=true&w=majority")

class Database():

    def __init__(self):
        self.username = os.getenv('MONGO_USER')
        self.password = os.getenv('MONGO_PASS')
        self.hostlist = os.getenv('MONGO_HOST')
        self.database = os.getenv('MONGO_DATA')
    
    def get_username(self):
        return self.username
