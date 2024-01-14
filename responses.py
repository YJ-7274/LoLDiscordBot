import random 



def get_response(message: str) -> str: 
  p_message = message.lower()

  if p_message == 'hello': 
    return 'Hello There!'
  
  if p_message == 'roll' :
    return str(random.randint(1,6))
  
  if p_message == 'list':
    return f"""
    ``` Here are my functions below!: 
    list - lists the available msf commands
    hello - returns a hello there message
    roll - rolls a dice (six sided and gives you the result)```
    """
  
  return 'I didn\'t understand what you wrote. Try typing "list".'