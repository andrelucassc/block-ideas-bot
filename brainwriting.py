import discord
from discord.ext import commands
import os
from database import Database
import logging
import datetime
import json
from bson import json_util
from metrics import Metrics
import requests

log = logging.getLogger('brainwriting')
pbilog = logging.getLogger('powerbi')

class Brainwriting(commands.Cog):
    """Category of Brainwriting"""
    def __init__(self):
        self.db = Database()
        self.metrics = Metrics()
        self.powerbi = PowerBI()
        self.collection = 'brainwriting_sessions'

    def currently_in_session(self):
        # is the brainwriting session started? TRUE=Yes and FALSE=No
        session_id = self.db.get_count(coll=self.collection) - 1
        log.info(f'currently_in_session: fetching data from last session ID: {session_id}')

        session = self.db.query(coll=self.collection, filtro={"id":session_id})
        log.debug(f'currently_in_session: session {session}')
        if session_id < 0:
            log.debug(f'currently_in_session: INIT: starting collection')
            return False
        elif session['finished'] == True or self.is_paused() == True:
            log.debug(f'currently_in_session: FINISHED: session retrieved sucessfully, ID {session_id}')
            return False
        else:
            log.debug(f'currently_in_session: IN_SESSION: session found but not finished, ID {session_id}')
            return True
    
    def is_paused(self):
        '''Checks if the session is paused
        
        :Returns:
          -  True: Paused
          -  False: Not Paused
        '''

        session_id = self.db.get_count(coll=self.collection) - 1
        log.debug(f'is_paused: fetching data from last session ID: {session_id}')

        session = self.db.query(coll=self.collection, filtro={"id":session_id})
        log.debug(f'is_paused: session {session}')

        if session_id < 0:
            log.debug(f'is_paused: INIT')
            return False
        elif session["paused"] == True:
            log.debug('is_paused: session is paused')
            return True
        else:
            log.debug('is_paused: session not paused')
            return False

    def kill_session(self):
        log.info('KILL_SESSION: ending session')
        message = "Finalizando Sessão"
        return message

    def iniciar_sessao(self):
        log.info('INICIAR_SESSAO: starting session message')
        message = "Iniciando sessão de brainwriting."
        return message
    
    def problema_sessao(self):
        log.info('PROBLEMA_SESSAO: problem message sent')
        return 'ERRO: Problema no Módulo de Brainwriting'
    
    @commands.command(name='start', help='MODERADOR: !start [nome_chat]:padrão=chat')
    @commands.has_role('admin')
    async def startBrainwriting(self, ctx, chat_name='chat'):
        guild = ctx.guild

        existing_chat = discord.utils.get(guild.channels, name=chat_name+'_1')
        
        if existing_chat:
            if self.is_paused():
                log.info('start: breaking paused session')
                await ctx.send(f'Reiniciando Sessão')

                session_id = self.db.get_count(coll=self.collection) - 1

                self.db.update_record(registro={ "id":session_id }, atualizacao={ "paused":False, "updated_at":datetime.datetime.now() }, coll=self.collection)

            elif not self.currently_in_session():
                log.info(f'START: starting brainwriting session')
                await ctx.send(self.iniciar_sessao())

                session_id = self.db.get_count(coll=self.collection)
                session_data = {"id":session_id, "finished":False, "paused":False, "started_at": datetime.datetime.now(), "updated_at":datetime.datetime.now(), "paused_at":None, "finished_at":None, "duration":0, "rodadas":0, "numb_ideas":0 }
                
                self.db.insert_db(coll=self.collection, doc=session_data)
            else:
                log.error(f'START: not possible to start or restart session. In Session: { self.currently_in_session() } Paused: { self.is_paused }')
                await ctx.send('Não foi possível iniciar ou reiniciar a sessão. O status da sessão está como já iniciada.')
        else:
            log.error(f'START: chat nao existente: {chat_name}_1')
            await ctx.send('Erro: não foi possível iniciar a sessão pois os canais de texto não foram criados')

    @commands.command(name='pause', help='MODERADOR: !pause - Pausa contagem do tempo até ser retomado')
    @commands.has_role('admin')
    async def pauseBrainwriting(self, ctx):

        session_id = self.db.get_count(coll=self.collection) - 1

        if self.currently_in_session():
            log.info(f'PAUSE: Pausing session ID: {session_id}')

            session_data = self.db.query(coll=self.collection, filtro={ "id":session_id })

            if session_data["duration"] != 0:
                # The paused_at is retrofeeded, when you start the document in python memory helps to produce `duration` but also deletes the old `paused_at` making it available for the next pause calculation.
                self.db.update_record(registro={ "id":session_id }, atualizacao={ "paused":True, "paused_at":datetime.datetime.now(), "duration":((datetime.datetime.now() - session_data["updated_at"]).total_seconds() + session_data["duration"])  }, coll=self.collection)
            else:
                self.db.update_record(registro={ "id":session_id }, atualizacao={ "paused":True, "paused_at":datetime.datetime.now(), "duration":(datetime.datetime.now() - session_data["started_at"]).total_seconds() }, coll=self.collection)
            
            await ctx.send('sessão pausada')

        else:
            log.error(f'PAUSE: not possible to pause session. Session: {self.currently_in_session()}. Paused: {self.is_paused()}.')
            await ctx.send(f'Erro ao pausar a sessão. Sessão Iniciada? {self.currently_in_session()}. Sessão Pausada? {self.is_paused()}.')

    @commands.command(name='stop', help='MODERADOR: !stop - Encerra a sessão')
    @commands.has_role('admin')
    async def stopBrainwriting(self, ctx):

        session_id = self.db.get_count(coll=self.collection) - 1
        number_of_ideas = [x["count"] for x in self.db.agregar(coll='raw_messages', pipeline=[
            {
                '$match': {
                    'session_id': session_id
                }
            }, {
                '$count': 'count'
            }
        ])]

        if self.currently_in_session():
            log.info(f'STOP: stopping brawriting session')
            await ctx.send(self.kill_session())

            session_data = self.db.query(coll=self.collection, filtro={ "id":session_id })
            if len(number_of_ideas) != 0:
                try:
                    self.db.update_record(coll=self.collection, registro={ "id":session_id }, atualizacao={ "finished": True, "finished_at":datetime.datetime.now(), "duration":((datetime.datetime.now() - session_data["updated_at"]).total_seconds()  + session_data["duration"]) , "rodadas":(session_data["rodadas"] + 1), "numb_ideas": number_of_ideas[0] })
                except Exception as e:
                    log.error('STOP: erro processando a sessao')
                    await ctx.send(f'Erro processando a sessão. Error: {e}')
            else:
                await ctx.send(f'Sessão encerrada sem ideias. Pulando processamento.')
        else:
            log.error('STOP: not possible to stop session')
            await ctx.send('STOP: não foi possível terminar a sessão, pois não tem nenhuma em sessão.')

    @commands.command(name='ideia', help='PARTICIPANTE: !ideia [ideia] - Envia uma ideia')
    async def send_idea(self, ctx, *args):
        if self.currently_in_session():
            log.info(f'IDEA: enviando ideia de {ctx.author.name}')
            log.info({"id":ctx.message.id, "author":ctx.message.author.name, "content":' '.join(args), "created_at":datetime.datetime.now(), "updated_at":None})
            session_id = self.db.get_count(coll=self.collection) - 1
            session_data = self.db.query(coll=self.collection, filtro={ "id":session_id })
            self.db.insert_db(coll='raw_messages', doc={"id":ctx.message.id, "author":ctx.message.author.name, "content":' '.join(args), "session_id":session_id, "chat_id":ctx.channel.id, "created_at":datetime.datetime.now(), "rodadas":session_data["rodadas"], "updated_at":None})
            await ctx.send('Ideia cadastrada com sucesso!')
        else:
            log.error(f'IDEA: could not send idea, because no session was started')
            await ctx.send('Erro ao enviar ideia. Nenhuma sessão ativa.')

    @commands.command(name='rotacionar', help='MODERADOR: !rotacionar [nome_chat]:padrão=chat')
    @commands.has_role('admin')
    async def rotate_ideas(self, ctx, chat_name='chat'):
        if self.currently_in_session():
            log.debug('ROTATE_IDEAS: rotating chats')

            guild = ctx.guild
            chats = guild.channels
            existing_chat = discord.utils.get(chats, name=chat_name+'_1')
            under_chats = []
            under_mesgs = {}
            session_id = self.db.get_count(coll=self.collection) - 1
            session_data = self.db.query(coll=self.collection, filtro={ "id":session_id })
            chats_messages = self.db.find(coll="raw_messages", filtro={"session_id":session_id})
            counter = 1 # To iterate between chats
            rodada_atual = session_data["rodadas"]
            log.info(f'rotacionar: rodada atual {rodada_atual}')

            if existing_chat:
                await ctx.send('iniciando rotação entre chats')
                log.debug(f'ROTATE_IDEAS: session_id {session_id}')

                number_of_mesgs = [x["num_mesgs"] for x in self.db.agregar(coll='raw_messages', pipeline=[{ "$match":{ "session_id":session_id } }, { "$count":"num_mesgs" }])]
                number_of_chats = [x["num_chats"] for x in self.db.agregar(coll='raw_messages', pipeline=[
                        {
                        '$match': {
                            'session_id': session_id
                        }
                    }, {
                        '$project': {
                            'chat_id': 1
                        }
                    }, {
                        '$group': {
                            '_id': 'null', 
                            'chats': {
                                '$addToSet': '$chat_id'
                            }
                        }
                    }, {
                        '$project': {
                            'num_chats': {
                                '$size': '$chats'
                            }
                        }
                    }
                ])]
                
                ratio = number_of_mesgs[0] % number_of_chats[0]
                log.info(f'ratio: {ratio}')

                log.info(f'ROTATE_IDEAS: number of messages: {number_of_mesgs}\nnum_chats: {number_of_chats}')

                for channel in chats:
                    if '_' in channel.name:
                        try:
                            log.debug(f'ROTATE_IDEAS: appending {channel.name}')
                            under_chats.append(channel)
                        except:
                            log.error('ROTATE_IDEAS: impossible to send|append message')
                    else:
                        log.debug('ROTATE_IDEAS: not a channel to rotate')

                for chat in under_chats:
                    under_mesgs[chat.name] = []

                log.debug(f'ROTATE_IDEAS: under_chats: {under_chats}')

                for message in chats_messages:
                    channel = discord.utils.get(guild.channels, id=message["chat_id"])
                    if message["rodadas"] == rodada_atual:
                        under_mesgs[channel.name].append(message["content"])

                log.info(f'ROTATE_IDEAS: under_mesgs: {under_mesgs}')
                
                for chat in under_chats:
                    log.debug(f'rotacionar: enviando mensagens para {chat.id}')
                    if counter == 1:
                        quantidade = len(under_mesgs[chat_name+'_'+str(number_of_chats[0])])
                        await chat.send(f'Quantidade de Ideias a serem analisadas: {quantidade}\n Rodada: {session_data["rodadas"] + 1}') # +1 pois ainda nao foi atualizado
                        for message in under_mesgs[chat_name+'_'+str(number_of_chats[0])]:
                            await chat.send(f'Ideia a ser analisada:\n--------\n{message}\n--------')
                    else:
                        quantidade = len(under_mesgs[chat_name+'_'+str(counter-1)])
                        await chat.send(f'Quantidade de Ideias a serem analisadas: {quantidade}\n Rodada: {session_data["rodadas"] + 1}')
                        for message in under_mesgs[chat_name+'_'+str(counter-1)]:
                            await chat.send(f'Ideia a ser analisada:\n--------\n{message}\n--------')
                    counter += 1

                self.db.update_record(registro={ "id":session_id }, atualizacao={ "rodadas":(session_data["rodadas"] + 1) }, coll=self.collection)
            else:
                await ctx.send(f'Channel \'{chat_name}\' não encontrado. Uso: !rotacionar [chat_name]')
        else:
            await ctx.send('Nenhuma sessão Iniciada ainda')
            log.error('ROTATE_IDEAS: no current session found')
        
    @commands.command(name='criar_objetivo', help='MODERADOR: !criar_objetivo [objetivo]')
    @commands.has_role('admin')
    async def cadastrar_objetivo(self, ctx, *args):
        if self.currently_in_session():
            log.info('CADASTRAR_OBJETIVO: cadastrando objetivos')
            
            # must be minus 1 because it already exists and references a session and not a objective itself
            session_id = self.db.get_count(coll=self.collection) - 1 

            existing_objective = self.db.query(coll='objectives', filtro={"id":session_id})

            if existing_objective:
                log.info(f'objective for {session_id} already created')
                await ctx.send('Erro: Objetivo já foi cadastrado!! Para cadastrar novo objetivo, inicie nova sessão.')
            else:
                self.db.insert_db(coll='objectives', doc={"session_id": session_id, "created_at":datetime.datetime.now(), "objetivo":' '.join(args)})

            guild = ctx.guild
            chats = guild.channels

            for chat in chats:
                if "_" in chat.name:
                    log.debug(f'CADASTRAR_OBJETIVO: enviando para {chat.name}')
                    conteudo = 'Objetivo da sessão cadastrado: ' + ' '.join(args) + """\nPara repassar uma ideia, por favor escreva em uma única mensagem seu texto junto do comando !ideia. \nNão há maneiras de editar as ideias enviadas, revise antes de enviar a ideia, por favor."""
                    await chat.send(content=conteudo)
                else:
                    log.debug(f'CADASTRAR_OBJETIVO: pass {chat.name}')

        else:
            log.error('CADASTRAR_OBJETIVO: nao foi possivel fazer o cadastro pois uma sessao nao foi iniciada.')
            await ctx.send('ERRO: Não foi possível fazer o cadastro')

    @commands.command(name='objetivo', help='PARTICIPANTE: !objetivo - mostra o objetivo da sessão')
    async def show_objetivo(self, ctx, *args):
        if self.currently_in_session():
            log.debug(f'OBJETIVO: consultando banco de objetivos')
            guild = ctx.guild
            session_id = self.db.get_count(coll=self.collection) - 1 

            log.debug(f'looking for session {session_id}')

            existing_objective = self.db.query(coll='objectives', filtro={"session_id":session_id})
            if existing_objective:
                log.debug(f'OBJETIVO: {existing_objective}')
                await ctx.send(content=existing_objective["objetivo"])
            else:
                await ctx.send(f'Sem objetivo cadastrado ainda para sessão {session_id}')
        else:
            log.error('OBJETIVO: nao foi possivel fazer o cadastro pois uma sessao nao foi iniciada.')
            await ctx.send('ERRO: Sessão não iniciada ainda.')


    @commands.command(name='pesquisar', help='PARTICIPANTE: !pesquisar - link de acesso ao módulo de pesquisa')
    async def pesquisar(self, ctx, *args):
        link = "https://app.powerbi.com/view?r=eyJrIjoiM2NhZDNhYTMtN2YwYS00NDgyLTkyYWEtMDNlMTczMDEyMzkzIiwidCI6ImYxYzM2NzE0LTgyNjAtNDhmNC1hOTU3LTI1OWZkOWQ1ZjVlMSJ9"
        await ctx.send(link)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            ctx.send("Argumento não aceito pelo bot.")

    
class PowerBI ():
    def __init__(self):
        self.application_id = os.getenv('APPLICATION_ID')
        self.application_secret = os.getenv('APPLICATION_SECRET')
        self.user_id = os.getenv('USER_ID')
        self.user_password = os.getenv('USER_PASSWORD')
        self.group_id = os.getenv('GROUP_ID')
        self.report_id = os.getenv('REPORT_ID')

    def get_embed_url(self, report_id, group_id):
        urlbase = "https://app.powerbi.com/reportEmbed?reportId={}&groupId={}&w=2&config=eyJjbHVzdGVyVXJsIjoiaHR0cHM6Ly9XQUJJLUJSQVpJTC1TT1VUSC1CLVBSSU1BUlktcmVkaXJlY3QuYW5hbHlzaXMud2luZG93cy5uZXQiLCJlbWJlZEZlYXR1cmVzIjp7Im1vZGVybkVtYmVkIjp0cnVlfX0%3d".format(report_id, group_id)
        return urlbase

    def get_access_token(self):
        data = {
            'grant_type': 'password',
            'scope': 'openid',
            'resource': "https://analysis.windows.net/powerbi/api",
            'client_id': self.application_id,
            'client_secret': self.application_secret,
            'username': self.user_id,
            'password': self.user_password
        }
        token = requests.post("https://login.microsoftonline.com/common/oauth2/token", data=data)
        assert token.status_code == 200, "Fail to retrieve token: {}".format(token.text)
        pbilog.info("Got access token: ")
        pbilog.info(token.json())
        return token.json()['access_token']


    def make_headers(self):
        return {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': "Bearer {}".format(self.get_access_token())
        }


    def get_embed_token_report(self, group_id, report_id):
        endpoint = "https://api.powerbi.com/v1.0/myorg/groups/{}/reports/{}/GenerateToken".format(group_id, report_id)
        headers = self.make_headers()
        res = requests.post(endpoint, headers=headers, json={"accessLevel": "View"})
        return res.json()['token']


    def get_groups(self):
        endpoint = "https://api.powerbi.com/v1.0/myorg/groups"
        headers = self.make_headers()
        return requests.get(endpoint, headers=headers).json()


    def get_dashboards(self, group_id):
        endpoint = "https://api.powerbi.com/v1.0/myorg/groups/{}/dashboards".format(group_id)
        headers = self.make_headers()
        return requests.get(endpoint, headers=headers).json()


    def get_reports(self, group_id):
        endpoint = "https://api.powerbi.com/v1.0/myorg/groups/{}/reports".format(group_id)
        headers = self.make_headers()
        return requests.get(endpoint, headers=headers).json()