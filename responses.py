import random 

def randomRunes():
  big_Runes = ['Precision', 'Sorcery', 'Domination', 'Resolve', 'Inspiration']
  Precision_Keystones = ['Press The Attack', 'Conqueror', 'Lethal Tempo', 'Fleet Footwork']
  Sorcery_Keystones = ['Summon Aery', 'Arcane Comet', 'Phase Rush']
  Domination_Keystones = ['Electrocute', 'Predator', 'Dark Harvest', 'Hail of Blades']
  Resolve_Keystones = ['Grasp of the Undying','Aftershock','Guardian']
  Inspiration_Keystones = ['Glacial Augment','Unsealed Spellbook','First Strike']

  runes = random.sample(big_Runes,2)
  
  keystone = ''
  match runes[0]: 
    case 'Precision': 
      keystone += random.sample(Precision_Keystones, 1)[0]
    case 'Sorcery':
      keystone += random.sample(Sorcery_Keystones, 1)[0]
    case 'Domination':
      keystone += random.sample(Domination_Keystones, 1)[0]
    case 'Resolve':
      keystone += random.sample(Resolve_Keystones, 1)[0]
    case default:
      keystone += random.sample(Inspiration_Keystones, 1)[0]
    
  return_value = f'{runes[0]} + {runes[1]}: Keystone = {keystone}'
  return return_value

def get_response(message: str) -> str: 
  p_message = message.lower()

  if p_message == 'hello': 
    return 'Hello There!'
  
  if p_message == 'roll' :
    return str(random.randint(1,6))
  
  if p_message == 'randomrunes':
    return randomRunes()
  
  if p_message == 'list':
    return f"""
    ``` Here are my functions below!: 
    list - lists the available msf commands
    hello - returns a hello there message
    roll - rolls a dice (six sided and gives you the result)
    randomRunes - generates a random combination of runes for your match. The subrunes are your choice ;D```
    """
  
  return 'I didn\'t understand what you wrote. Try typing "list".'