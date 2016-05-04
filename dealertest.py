
from catan.card_dealer import CardDealer



def process_token(token, camera):
  if token == 'AWB':
    val1 = raw_input("Val1: ")
    val2 = raw_input("Val2: ")
    camera.set_setting(token, (float(val1), float(val2)))
  elif token == 'ZOOM':
    print "Not supported yet."
  elif token == 'RESOLUTION':
    val1 = raw_input("W: ")
    val2 = raw_input("H: ")
    camera.set_setting(token, (int(val1), int(val2)))
  else:
    value = raw_input("New value: ")
    camera.set_setting(token, int(value))



def main():
  resources = ['WHEAT', 'SHEEP', 'BRICK', 'IRON', 'WOOD']
  players = ['GREEN', 'RED', 'BLUE', 'BROWN']
  instructions = {p: {r: 0 for r in resources} for p in players}

  dealer = CardDealer()

  while (True):
    print "Enter a player (RED, GREEN, BLUE, BROWN),\nresource (SHEEP, WHEAT, IRON, WOOD, BRICK),\nand quantity to deal."
  
    player = raw_input("Player: ")
    resource  = raw_input("Resource: ")
    quantity = raw_input("Quantity: ")

    try:
      instructions[player.upper()][resource.upper()] = quantity

      dealer.process_round(instructions)

      instructions[player.upper()][resource.upper()] = 0
    except Exception as e:
      print "INVALID, try again."





if __name__ == "__main__":
  main()
