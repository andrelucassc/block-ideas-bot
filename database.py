import os
from pymongo import MongoClient
import json
from data import *
import logging 
from bson.json_util import dumps
import datetime

log = logging.getLogger('database')

class Database():
    # Creates a Database Handler for Mongo
    def __init__(self):
        # Creates Database Attributes
        self.username   = os.getenv('MONGO_USER')
        self.password   = os.getenv('MONGO_PASS')
        self.hostlist   = os.getenv('MONGO_HOST')
        self.database   = os.getenv('MONGO_DATA')
        self.uri        = os.getenv('MONGO_URI')
    
    def query(self, coll, filtro):
        # Method to query the database
        log.debug('query: being executed')
        cons = self.get_connection()
        db = cons.tcc
        co = db[coll]

        return co.find_one(filtro)

    def find(self, coll, filtro):
        '''Method to query the DB and find all iterables'''
        if coll:
            log.debug('FIND: querying the database')
            cons = self.get_connection()
            db = cons.tcc
            co = db[coll]

            return co.find(filtro)
        else:
            log.error('FIND: no collection determined to be searched')
    
    def update_record(self, registro, atualizacao, coll=None):
        # Method to update one record in the database
        if not coll:
            log.error('Empty Collection sent! Cannot get count of documents.')
        else:
            log.info('updating record sent')
            cons = self.get_connection()
            db = cons.tcc
            co = db[coll]

            co.update_one(registro, {"$set": atualizacao})

    def get_count(self, coll=None):
        '''count the number of lines of the collection'''
        # Returns a method to count the number of lines of the connection
        if not coll:
            log.error('Empty Collection sent! Cannot get count of documents.')
        else:
            cons = self.get_connection()
            db = cons.tcc
            co = db[coll]
            return co.estimated_document_count()

    def insert_db(self, coll=None, doc=None):
        '''insert_one method'''
        # Method to insert into the database without calling the connection itself
        if not coll:
            log.error('Empty Collection sent! Cannot get count of documents.')
        else:
            cons = self.get_connection()
            db = cons.tcc
            co = db[coll]

            try:
                insert_result = co.insert_one(doc)
                log.info(f'inserted into the database')
                return insert_result
            except TypeError:
                log.error('INSERT_DB: TypeError: error inserting line')
                return False
            except Exception as e:
                log.error(f'INSERT_DB: {e}')
                return False

    def is_json(self, json_test):
        # tests for json valid type
        try:
            json_obj = json.loads(json_test)
        except:
            log.error(f'ValueError: Not a valid JSON TYPE passed to the database!')
            return False
        return True

    def get_connection(self):
        # Returns the Mongo Client Driver
        log.debug('connecting to the database')

        return MongoClient("mongodb+srv://"+self.get_username()+":"+self.password+"@"+self.hostlist+"/"+self.database+"?retryWrites=true&w=majority")

    def get_username(self):
        # Returns the Username used in the database
        return self.username
     
    def del_message(self, message, connection):
        # Deletes the line inserted into Mongo
        log.info('deleted message from the database')

        msg_id = message.id
        
        db = connection.tcc
        raw_messages = db.raw_messages

        query = {"id": msg_id}

        raw_messages.delete_one(query)
    
    def agregar(self, coll, pipeline):
        '''Method to aggregate data from db'''
        cons = self.get_connection()
        db = cons.tcc
        co = db[coll]
        try:
            return co.aggregate(pipeline)
        except Exception as e:
            log.error(f'databaseError: {e}')



