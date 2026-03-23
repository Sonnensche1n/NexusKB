from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from server.db.DbManager import session_scope
from server.api.BaseApi import BaseApi
from sqlalchemy import select, delete
from server.model.orm_knb import ChatInfo, ChatMesg
from server.model.entity_knb import ChatInfo as ChatInfoEntity, ChatMesg as ChatMesgEntity, ReposSetting as ReposSettingEntity
from datetime import datetime
from server.core.tools.ask_to_llm import ask_to_llm_stream
from server.utils.websocketutils import WebsocketManager
from server.core.tools.message_tools import message_entity_to_json
from server.core.knb.ReposService import ReposService

class ChatApi(BaseApi):
  reposService = ReposService()
  def __init__(self, app: FastAPI, manager: WebsocketManager):
    BaseApi.__init__(self)
    
    # 查询对话列表
    @app.post('/knb/chat/list')
    def chatList(chatInfo: ChatInfoEntity):
      reposId = chatInfo.reposId
      stmt = select(ChatInfo).where(ChatInfo.reposId == reposId).order_by(ChatInfo.lastTm.desc())
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    # 查询我的对话列表
    @app.post('/knb/chat/my/list')
    def chatList(chatInfo: ChatInfoEntity, request: Request):
      reposId = chatInfo.reposId
      stmt = select(ChatInfo).where(ChatInfo.reposId == reposId, ChatInfo.crtUser == self.getUserId(request)).order_by(ChatInfo.lastTm.desc())
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    # 新增对话
    @app.post('/knb/chat')
    def addChat(chatInfo: ChatInfoEntity, request: Request):
      chatInfo.chatId = self.getPk()
      chatInfo.crtTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      chatInfo.lastTm = chatInfo.crtTm
      chatInfo.crtUser = self.getUserId(request)
      orm = ChatInfo(
        chatId = chatInfo.chatId,
        reposId = chatInfo.reposId,
        chatTtl = chatInfo.chatTtl,
        crtUser = chatInfo.crtUser,
        crtTm = chatInfo.crtTm,
        lastTm = chatInfo.lastTm
      )
      with session_scope() as session:
        session.add(orm)
      return self.success(chatInfo)
    
    # 修改对话
    @app.put('/knb/chat')
    def editChat(chatInfo: ChatInfoEntity):
      chatId = chatInfo.chatId
      with session_scope() as session:
        orm = session.get(ChatInfo, chatId)
        orm.chatTtl = chatInfo.chatTtl
        orm.lastTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session.merge(orm)
      return self.success()

    # 删除对话
    @app.delete('/knb/chat/{id}')
    def removeChat(id):
      with session_scope() as session:
        orm = session.get(ChatInfo, id)
        session.delete(orm)
      return self.success()
    
    # 删除对话
    @app.delete('/knb/chat/message/clear/{id}')
    def clearChatMessage(id):
      with session_scope() as session:
        stmt = delete(ChatMesg).where(ChatMesg.chatId == id)
        session.execute(stmt)
      return self.success()
    
    # 查询对话消息列表
    @app.post('/knb/chat/message/list')
    def messageList(chatMesg: ChatMesgEntity):
      chatId = chatMesg.chatId
      stmt = select(ChatMesg).where(ChatMesg.chatId == chatId).order_by(ChatMesg.crtTm.asc())
      list = []
      with session_scope(True) as session:
        for row in session.scalars(stmt):
          list.append(row)
      return self.success(list)
    
    # 删除对话消息
    @app.delete('/knb/chat/message/{id}')
    def removeMessage(id:str):
      with session_scope() as session:
        stmt = delete(ChatMesg).where((ChatMesg.mesgId == id) | (ChatMesg.mesgPid == id))
        session.execute(stmt)
      return self.success()
    
    # 重新生成消息
    @app.post('/knb/chat/remessage')
    def reMessage(request: Request, mesg: ChatMesgEntity, history: list[ChatMesgEntity] = []):
      reposId = mesg.reposId
      userId = self.getUserId(request=request)
      with session_scope(True) as session:
        orm = session.query(ChatMesg).filter(ChatMesg.mesgPid == mesg.mesgId).first()
        if (orm is None):
          childMesg = ChatMesgEntity(
            mesgId = self.getPk(),
            mesgPid = mesg.mesgId,
            reposId = reposId,
            chatId = mesg.chatId,
            mesgTyp = mesg.mesgTyp,
            crtRole = 'sys'
          )
        else:
          childMesg = ChatMesgEntity().copy_from_dict(orm.to_dict())
      setting = self.reposService.get_repos_setting(reposId)
      def event_generator():
        yield message_entity_to_json(childMesg.to_dict())
        for message in ask_to_llm_stream(setting=setting, chatMesg=childMesg, question=mesg.mesgCntnt, userId=userId, chatHistory=history):
          yield message
      return EventSourceResponse(event_generator())
    # 新增对话消息
    @app.post('/knb/chat/message')
    def addMessage(request: Request, mesg: ChatMesgEntity, history: list[ChatMesgEntity] = []):
      reposId = mesg.reposId
      mesg.mesgId = self.getPk()
      mesg.crtTm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      mesg.mesgTyp = 'text'
      mesg.crtRole = 'usr'
      userId = self.getUserId(request=request)
      mesg.crtUser = userId
      orm = ChatMesg().copy_from_dict(vars(mesg))
      mesgId = self.getPk()
      childMesg = ChatMesgEntity(
        mesgId = mesgId,
        mesgPid = mesg.mesgId,
        reposId = reposId,
        chatId = mesg.chatId,
        mesgTyp = mesg.mesgTyp,
        crtRole = 'sys'
      )
      with session_scope() as session:
        session.add(orm)
      setting = self.reposService.get_repos_setting(reposId)
      def event_generator():
        yield message_entity_to_json(childMesg.to_dict())
        for message in ask_to_llm_stream(setting=setting, chatMesg=childMesg, question=mesg.mesgCntnt, userId=userId, chatHistory=history):
          yield message
      return EventSourceResponse(event_generator())
    
    # 修改对话消息
    @app.put('/knb/chat/message')
    def editMessage(chatMesg: ChatMesgEntity):
      mesgId = chatMesg.mesgId
      with session_scope() as session:
        orm = session.get(ChatMesg, mesgId)
        orm.mesgCntnt = chatMesg.mesgCntnt
        session.merge(orm)
      return self.success()