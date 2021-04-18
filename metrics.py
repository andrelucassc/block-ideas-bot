# metrics.py
from discord.ext import commands
from database import Database
from etl import Etl
import logging

log = logging.getLogger('metrics')

class Metrics():
    '''To call Metrics'''
    def __init__(self):
        self.db = Database()
        self.etl = Etl()
        self.last_session = self.db.get_count(coll='brainwriting_sessions') - 1

    def get_session(self, session):
        '''Returns the session document in the database
        
        :Parameters:
          -  `session`: (Optional) - 'last' pega a última sessão
        
        :Returns:
          -  instance of pymongo.document
        '''
        if session:
            log.info(f'get_session: ID: {session}')
            return self.etl.get_session_data(session_id=session)
        elif self.last_session < 0:
            log.info(f'get_session: ID: 0')
            return self.etl.get_session_data(session_id=0)
        else:
            log.info(f'get_session: ID: {self.last_session}')
            return self.etl.get_session_data(session_id=self.last_session)

    def put_wit_session(self, session='last'):
        session_id = self.db.get_count(coll='brainwriting_sessions') - 1
        try:
            if session == 'last':
                log.info(session_id)
                
                self.etl.process_ideas_wit(session_id=session_id)
                
            else:
                log.info(session)
                self.etl.process_ideas_wit(session_id=int(session))
            return True
        except Exception as e:
            log.error(f'WitError: {e}')
            return Exception

    def put_gcp_session(self, session='last'):
        session_id = self.db.get_count(coll='brainwriting_sessions') - 1
        try:
            if session == 'last':
                log.info(session_id)
                
                self.etl.process_ideas_gcp(session_id=session_id)
                
            else:
                log.info(session)
                self.etl.process_ideas_gcp(session_id=int(session))
            return True

        except Exception as e:
            log.error(f'GcpError: {e}')
            return Exception

class MetricsCog(commands.Cog):
    '''Command wrapper for Metrics'''
    def __init__(self):
        self.metrics = Metrics()
    
    @commands.command(name='sessao', help='ADMIN: !sessao [session]:default=last')
    @commands.has_role('admin')
    async def get_session(self, ctx, session=None):
        session_data = self.metrics.get_session(session=session)
        if session_data:
            await ctx.send(session_data)
        else:
            await ctx.send(f'Sessão {session} não encontrada.')
    
    @commands.command(name='wit', help='ADMIN: !wit [session]:default=last - API do WIT')
    @commands.has_role('admin')
    async def put_wit_session(self, ctx, session='last'):
        result = self.metrics.put_wit_session(session=session)
        if result:
            await ctx.send('Wit Processado')
        else:
            log.error(f'{result}')
            await ctx.send('Erro processando no Wit')

    @commands.command(name='gcp', help='ADMIN: !gcp [session]:default=last - API do GCP')
    @commands.has_role('admin')
    async def put_gcp_session(self, ctx, session='last'):
        result = self.metrics.put_gcp_session(session=session)
        if result:
            await ctx.send('gcp processado')
        else:
            log.error(f'{result}')
            await ctx.send('Erro processando no GCP')