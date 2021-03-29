import os
from pymongo import MongoClient
import json
from data import *
    
class Database():
    # Creates a Database Handler for Mongo
    def __init__(self):
        # Creates Database Attributes
        self.username   = os.getenv('MONGO_USER')
        self.password   = os.getenv('MONGO_PASS')
        self.hostlist   = os.getenv('MONGO_HOST')
        self.database   = os.getenv('MONGO_DATA')
        self.uri        = os.getenv('MONGO_URI')
        self.collection = "messages_raw"
    
    def get_connection(self):
        # Returns the Mongo Client Driver
        return MongoClient("mongodb+srv://"+self.get_username()+":"+self.password+"@"+self.hostlist+"/"+self.database+"?retryWrites=true&w=majority")

    def get_username(self):
        # Returns the Username used in the database
        return self.username

    def put_message(self, message, connection):
        # Inserts one document into the database
        msg_id = message.id
        msg_content = message.content
        msg_author = message.author.name
        msg_created = change_tz(message.created_at)
        
        # Setting the locale of message storage
        db = connection.tcc
        raw_messages = db.raw_messages

        insert_result = raw_messages.insert_one({"id": msg_id, "author": msg_author, "content": msg_content, "created_at": msg_created})
        
    def del_message(self, message, connection):
        # Deletes the line inserted into Mongo
        msg_id = message.id
        
        db = connection.tcc
        raw_messages = db.raw_messages

        query = {"id": msg_id}

        raw_messages.delete_one(query)



