import json

def message_quote_to_json(mesgId:str, chatId:str, reposId:str, quotes) -> str:
  message = {
    'type': 'chat_message_quote', 'data': {
      'mesgId': mesgId, 'chatId': chatId, 'reposId': reposId, 'quotes': quotes
    }
  }
  return json.dumps(message, ensure_ascii=False)

def message_chunk_to_json(chunk) -> str:
  message = {
    'type': 'chat_message_chunk', 'data': chunk
  }
  return json.dumps(message, ensure_ascii=False)

def message_content_to_json(message) -> str:
  message = {
    'type': 'chat_message_content', 'data': message
  }
  return json.dumps(message, ensure_ascii=False)

def message_entity_to_json(message) -> str:
  message = {
    'type': 'chat_message_entity', 'data': message
  }
  return json.dumps(message, ensure_ascii=False)

def message_error_to_json(error) -> str:
  message = {
    'type': 'chat_message_error', 'data': error
  }
  return json.dumps(message, ensure_ascii=False)