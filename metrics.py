# metrics.py
from discord.ext import commands
from database import Database
from etl import Etl
import logging

log = logging.getLogger('metrics')

class Metrics(commands.Cog):
    '''To call Metrics'''
    def __init__(self):
        self.db = Database()
        self.etl = Etl()
    
    @commands.command(name='get_session', help='!')
    @commands.has_role('admin')
    async def get_session(self, ctx, session='last'):
        guild = ctx.guild
        session_id = self.db.get_count(coll='brainwriting_sessions') - 1

        if session == 'last':
            log.info(session_id)
            await ctx.send(self.etl.get_session_data(session_id=session_id))
        else:
            log.info(session)
            await ctx.send(self.etl.get_session_data(session_id=int(session)))
        
    @commands.command(name='process_session', help='!')
    @commands.has_role('admin')
    async def process_session(self, ctx, session='last'):
        guild = ctx.guild
        session_id = self.db.get_count(coll='brainwriting_sessions') - 1

        if session == 'last':
            log.info(session_id)
            session_data = self.etl.get_session_data(session_id=session_id)
        else:
            log.info(session)
            session_data = self.etl.get_session_data(session_id=int(session))
        try:
            result = self.etl.process_session_data(coll='session_data', session_data=session_data)
            await ctx.send(f'result: {result.acknowledged}')
        except Exception as e:
            log.error(f'{e}')
            await ctx.send('Problem Processing session data')
    
    @commands.command(name='wit_session', help='!')
    @commands.has_role('admin')
    async def put_wit_session(self, ctx, session='last'):
        guild = ctx.guild
        session_id = self.db.get_count(coll='brainwriting_sessions') - 1
        try:
            if session == 'last':
                log.info(session_id)
                
                self.etl.process_ideas_wit(session_id=session_id)
                
            else:
                log.info(session)
                self.etl.process_ideas_wit(session_id=int(session))
        except Exception as e:
            log.error(f'WitError: {e}')

    @commands.command(name='gcp_session', help='!')
    @commands.has_role('admin')
    async def put_gcp_session(self, ctx, session='last'):
        guild = ctx.guild
        session_id = self.db.get_count(coll='brainwriting_sessions') - 1
        try:
            if session == 'last':
                log.info(session_id)
                
                self.etl.process_ideas_gcp(session_id=session_id)
                
            else:
                log.info(session)
                self.etl.process_ideas_gcp(session_id=int(session))
        except Exception as e:
            log.error(f'GcpError: {e}')
