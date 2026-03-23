from fastapi import WebSocket
from typing import List
 
"""
创建工具管理类 处理服务端和客户端的交互
"""
class WebsocketManager:
  def __init__(self):
    # 初始化参数 记录活跃的客户端
    self.active_clients: dict = {}

  # client_id 是 token
  def connect(self, client_id: str, websocket: WebSocket):
    self.active_clients[client_id] = websocket
 
  def disconnect(self, client_id: str):
    # 断开某个客户端的连接
    self.active_clients.pop(client_id)
 
  async def send_message_to_client(self, message: str, websocket: WebSocket):
    # 给客户端发送消息
    await websocket.send_text(message)
  
  async def send_message_to_client_id(self, message: str, client_id: str):
    # 给客户端发送消息
    if (client_id in self.active_clients):
      await self.active_clients[client_id].send_text(message)
 
  async def broadcast(self, message: str):
    # 给所有客户端发送消息 广播
    for websocket in self.active_clients.values():
      await websocket.send_text(message)