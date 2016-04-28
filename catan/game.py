
from catan.config import CVConfig
from catan.detection.board import BoardDetector
from catan.detection.dice import DiceDetector

class CatanomousGame(object):


  def __init__(self, config):
    self._board_detector = None
    self._config = config
    return


  def init_game(self, hex_img):
    self._board_detector = BoardDetector(self._config, hex_img)
    return self._board_detector._hexagons  #TODO temporary, remove this

  def new_game(self, resource_img, number_img):
    self._board_detector.reset_res_and_num()
    self._board_detector.detect_resources(resource_img)
    self._board_detector.detect_numbers(number_img)
    return self._board_detector._hexagons # TODO temporary?

  def save_hexagons(self, filename):
    self._config.set_hexagons(self._board_detector.get_hex_contours())
    self._config.save_hex_config(filename)

  def dice_rolled(self, num, updated_img):
    # Return instructions for card dealing
    detected = self._board_detector.detect_properties(updated_img)
    robber_tile = self._board_detector.detect_robber(updated_img)

    resources = ['WHEAT', 'SHEEP', 'BRICK', 'IRON', 'WOOD']
    players = ['GREEN', 'RED', 'BLUE', 'BROWN']
    instructions = {p: {r: 0 for r in resources} for p in players}
    for (tile, plist) in detected:
      if num == tile.get_num() and tile != robber_tile:
        for (pt, player) in plist:
          count = 2 if player.isupper() else 1
          instructions[player.upper()][tile.get_res()] += count

    print instructions

    return detected #TODO temporary, remove this


