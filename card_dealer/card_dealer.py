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
#

import wiringpi

instruction = ''
playerDict = {
              'GREEN' : '0', 
              'BROWN' : '1', 
              'RED' : '2', 
              'BLUE' : '3'
             }
resourceDict = {
                'WOOD' : 'D', 
                'BRICK' : 'B', 
                'IRON' : 'O', 
                'SHEEP' : 'S', 
                'WHEAT' : 'W'
               }

# GREEN, BROWN, RED, BLUE
# WHEAT, IRON, BRICK, WOOD, SHEEP
# {player: {resource: count}} 

def setupCardDealer():
    wiringpi.wiringPiSPISetup(1,500000)
    # No need to send initalization byte

# If there's only one method to use, it's this one!
def processRound(instrDict):
    # Every key is a player 
    for p, resources in instrDict.items():
        setPlayer(playerDict[p])
        # Iterate over player's resources,
        for res, count in resources.items():
            if (count > 0):
                giveResource(resourceDict[res], count)

    # Send instruction to card dealer
    sendAndClearInstruction()


def sendAndClearInstruction():
    global instruction
    wiringpi.wiringPiSPIDataRW(1, instruction + '\n')
    instruction = ''
    
def setPlayer(p):
    global instruction
    instruction += p

def giveResource(resource, n):
    global instruction
    instruction += resource + str(n)
    
# Run game
setupCardDealer()

# processRound({
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
# print (instruction)


