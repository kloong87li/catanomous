
from catan.config import CVConfig
from catan.detection.board import BoardDetector
from catan.detection.dice import DiceDetector

class CatanomousGame(object):


  def __init__(self, config):
    self._board_detector = None
    self._dice_detector = None
    self._config = config

    return


  def new_game(self, hex_img, color_img):
    self._board_detector = BoardDetector(self._config, hex_img, color_img)
    self._dice_detector = DiceDetector(self._config)
    return self._board_detector._hexagons  #TODO temporary, remove this


  def save_hexagons(self, filename):
    self._config.set_hexagons(self._board_detector.get_hex_contours())
    self._config.save_hex_config(filename)


  def update_properties(self, updated_img):
    properties = self._board_detector.detect_properties(updated_img)
    return properties #TODO temporary, remove this


  # Returns obj indicating what resources to distribute
  def dice_rolled(self, dice_img):
    num = self._dice_detector.detect_roll(dice_img)
    return



