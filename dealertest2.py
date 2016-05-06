
from catan.card_dealer import CardDealer





def main():
  resources = ['WHEAT', 'SHEEP', 'BRICK', 'IRON', 'WOOD']
  players = ['GREEN', 'RED', 'BLUE', 'BROWN']
  instructions = {p: {r: 0 for r in resources} for p in players}

  dealer = CardDealer()

  while (True):
    raw_input("1")
    instructions["BLUE"]["BRICK"] = 1
    instructions["RED"]["WOOD"] = 1
    dealer.process_round(instructions)
    instructions["BLUE"]["BRICK"] = 0
    instructions["RED"]["WOOD"] = 0

    raw_input("2")
    instructions["BLUE"]["WOOD"] = 3
    instructions["RED"]["IRON"] = 2
    dealer.process_round(instructions)
    instructions["BLUE"]["WOOD"] = 3
    instructions["RED"]["IRON"] = 2






if __name__ == "__main__":
  main()
