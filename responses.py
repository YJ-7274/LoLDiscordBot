import random 

def get_response(message: str) -> str: 
  p_message = message.lower()

  if p_message == 'hello': 
    return 'Hello There!'
  
  if p_message == 'roll' :
    return str(random.randint(1,6))
  
  if p_message == '!help':
    return '`Here are my functions below!.`'
  
  return 'I didn\'t understand what you wrote. Try typing "!help".'