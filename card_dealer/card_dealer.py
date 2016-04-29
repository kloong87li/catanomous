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

instruction = ''
player_dict = {
              'GREEN' : '0', 
              'BROWN' : '1', 
              'RED' : '2', 
              'BLUE' : '3'
             }
resource_dict = {
                'WOOD' : 'D', 
                'BRICK' : 'B', 
                'IRON' : 'O', 
                'SHEEP' : 'S', 
                'WHEAT' : 'W'
               }

def setup_card_dealer():
    wiringpi.wiringPiSPISetup(1,500000)
    # No need to send initalization byte

# If there's only one method to use, it's this one!
def process_round(instrDict):
    # Every key is a player 
    for p, resources in instrDict.items():
        _set_player(player_dict[p])
        # Iterate over player's resources,
        for res, count in resources.items():
            if (count > 0):
                _give_resource(resource_dict[res], count)

    # Send instruction to card dealer
    _send_and_clear_instruction()


def _send_and_clear_instruction():
    global instruction
    wiringpi.wiringPiSPIDataRW(1, instruction + '\n')
    instruction = ''
    
def _set_player(p):
    global instruction
    instruction += p

def _give_resource(resource, n):
    global instruction
    instruction += resource + str(n)
    
# Run game
setup_card_dealer()

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