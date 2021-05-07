# etl.py
import logging
from database import Database
from wit import Wit
import os
from google.cloud import language_v1
import json
import proto
from constants import gcp_types

log = logging.getLogger('etl')

class Etl():
    '''Queries and does ETL to the app data'''
    def __init__(self):
        self.db = Database()
        self.wit = Wit(os.getenv('WIT_TOKEN'), logger=log)
        self.gcp = language_v1.LanguageServiceClient()

    def get_session_data(self, session_id):
        '''Returns Mongo Document of the Session ID specified.
        
        :Parameters:
          -  `session_id`
        '''
        log.debug('get_session_data: starting')
        try:
            session_doc = self.db.query(coll='brainwriting_sessions',filtro={"id":session_id})
            return session_doc
        except Exception as e:
            log.error(f'{e}')
            return e
    
    def process_ideas_wit(self, session_id):
        '''Method to pass idea to the wit API and register it'''
        log.debug('process_idea_wit: starting')

        messages = self.db.find(coll='raw_messages', filtro={"session_id":session_id})
        
        for message in messages:
            response = self.wit.message(message["content"])
            log.debug(f'response {response}')
            self.db.insert_db(coll='wit_response', doc={"session_id":session_id, "message":message["content"], "intent":response["intents"], "entities":response["entities"], "traits":response["traits"]})    

    def process_ideas_gcp(self, session_id):
        '''Method to pass idea to GCP'''
        log.debug('process idea GCP: starting')

        messages = self.db.find(coll='raw_messages', filtro={"session_id":session_id})

        for message in messages:
            document = language_v1.Document(content=message["content"], type_=language_v1.Document.Type.PLAIN_TEXT)
            try:
                entities = json.loads(proto.Message.to_json(self.gcp.analyze_entities(request={'document': document})))
            except Exception as e:
                log.error(e)
            syntax = json.loads(proto.Message.to_json(self.gcp.analyze_syntax(request={'document': document})))
            log.debug(f'response {type(entities)}')
            self.db.insert_db(coll='gcp_response', doc={"session_id":session_id, "message":message["content"], "entities":entities["entities"], "language_text":entities["language"], "syntax":syntax})


