import os
from pymongo import MongoClient
import json
from data import *
import logging 
from bson.json_util import dumps
import datetime

log = logging.getLogger('database')

class Database():
    """Database Object to wrap MongoDB"""
    # Creates a Database Handler for Mongo
    def __init__(self):
        # Creates Database Attributes
        self.username   = os.getenv('MONGO_USER')
        self.password   = os.getenv('MONGO_PASS')
        self.hostlist   = os.getenv('MONGO_HOST')
        self.database   = os.getenv('MONGO_DATA')
        self.uri        = os.getenv('MONGO_URI')
        self.connection = self.get_connection()
        self.dataname   = self.connection.tcc
    
    def query(self, coll, filtro):
        '''Method to query the database
        
        :Parameters:
          -  `coll`
          -  `filtro`
        '''
        log.debug('query: being executed')
        co = self.dataname[coll]

        return co.find_one(filtro)

    def find(self, coll, filtro):
        '''Method to query the DB and find all iterables
        
        :Parameters:
          - `coll`
          - `filtro`
        '''

        log.debug('find: querying the database')
        co = self.dataname[coll]
        return co.find(filtro)

    def update_record(self, registro, atualizacao, coll=None):
        ''' Method to update ONE record in the database.
        
        :Parameters:
          -  `registro`: Filter to identify ONE document
          -  `atualizacao`: Field to be updated
          -  `coll`: Collection affected

        :Returns:
          -  An instance of pymongo.updateResults
        '''

        log.debug('update_record: updating record sent')
        co = self.dataname[coll]
        results = co.update_one(filter=registro, update={"$set": atualizacao})
        return results

    def get_count(self, coll=None):
        '''count the number of documents of the collection
        
        :Parameters:
          -  `coll`
        '''

        co = self.dataname[coll]
        return co.estimated_document_count()

    def insert_db(self, coll=None, doc=None):
        '''insert_one method.
        
        :Parameters:
          -  `coll`
          -  `doc`
        '''

        co = self.dataname[coll]

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
        '''tests for json valid type
        
        :Parameters:
          -  `json_test`: The JSON to be validated
        '''

        try:
            json_obj = json.loads(json_test)
            return True
        except:
            log.error(f'ValueError: Not a valid JSON TYPE passed to the database!')
            return False

    def get_connection(self):
        '''Returns the Mongo Client Driver'''
        log.debug('connecting to the database')

        return MongoClient("mongodb+srv://"+self.get_username()+":"+self.password+"@"+self.hostlist+"/"+self.database+"?retryWrites=true&w=majority")

    def get_username(self):
        '''Returns the Username used in the database'''
        return self.username
     
    def del_message(self, message, connection):
        '''Deletes the line inserted into Mongo
        
        :Parameters:
          -  `message`
          -  `connection`
        '''
        log.debug('deleted message from the database')

        msg_id = message.id
        
        raw_messages = self.dataname.raw_messages

        query = {"id": msg_id}

        raw_messages.delete_one(query)
    
    def agregar(self, coll, pipeline):
        '''Method to aggregate data from db
        
        :Parameters:
          -  `coll`
          -  `pipeline`
        '''

        co = self.dataname[coll]
        try:
            return co.aggregate(pipeline)
        except Exception as e:
            log.error(f'databaseError: {e}')
            return e
