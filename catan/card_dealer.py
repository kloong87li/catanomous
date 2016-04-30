# Current protocol:
#
# Command of the form 'PANBNCN...' will be sent via spi following these rules:
# P    - The player will range from 0-3 to indicate which
#        player we're feeding cards to
# AN.. - The first letter (could be from [D, B, O, S, W] points to a resource,
#        wheras N is the number of that resource to dispense.
#        The resources are: 
#        'D' -> Wood (D in the word Wood)
#        'B' -> Brick
#        'O' -> Iron (Originally Ore. Gosh Ken.)
#        'S' -> Sheep
#        'W' -> Wheat
#
# For example, 
#
# for 2 woods and 1 sheep to player 0, 
# we'll send "0S2W1\n"
#
# for 2 woods and 1 sheep to player 0, and 1 brick for player 1 
# we'll send "0S2W11B1\n"


import wiringpi


class CardDealer(object):
  _PLAYER_DICT = {
              'GREEN' : '0', 
              'BROWN' : '1', 
              'RED' : '2', 
              'BLUE' : '3'
             }

  _RESOURCE_DICT = {
                  'WOOD' : 'D', 
                  'BRICK' : 'B', 
                  'IRON' : 'O', 
                  'SHEEP' : 'S', 
                  'WHEAT' : 'W'
                 }

  def __init__(self):
      wiringpi.wiringPiSPISetup(1, 500000)
      # No need to send initalization byte

  # If there's only one method to use, it's this one!
  def process_round(self, instrDict):
      instruction = ''
      # Every key is a player 
      for p, resources in instrDict.items():
          instruction += self._PLAYER_DICT[p]
          # Iterate over player's resources,
          for res, count in resources.items():
              if (count > 0):
                  instruction += self._RESOURCE_DICT[res] + str(count)

      # Send instruction to card dealer
      self._send_instruction(instruction)

  def _send_instruction(self, instruction):
      wiringpi.wiringPiSPIDataRW(1, instruction + '\n')
    
# Run game
# setup_card_dealer()

# Example round
#
# process_round({
#               'GREEN' : 
#                         {
#                             'WOOD' : 1, 
#                             'BRICK' : 0, 
#                             'IRON' : 0, 
#                             'SHEEP' : 0, 
#                             'WHEAT' : 0
#                         },
#               'BROWN' : 
#                         {
#                             'WOOD' : 1, 
#                             'BRICK' : 1, 
#                             'IRON' : 0, 
#                             'SHEEP' : 0, 
#                             'WHEAT' : 0
#                         },
#               'RED' : 
#                         {
#                             'WOOD' : 1, 
#                             'BRICK' : 1, 
#                             'IRON' : 1, 
#                             'SHEEP' : 0, 
#                             'WHEAT' : 0
#                         },
#               'BLUE' : 
#                         {
#                             'WOOD' : 1, 
#                             'BRICK' : 1, 
#                             'IRON' : 1, 
#                             'SHEEP' : 1, 
#                             'WHEAT' : 0
#                         },
#              })