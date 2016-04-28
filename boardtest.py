import cv2
import imutils
import numpy as np
from PIL import Image

import argparse, time

from utils.cv import CVUtils
from utils.gui import GUIUtils
from catan.config import CVConfig
from catan.game import CatanomousGame
from utils.debug import Debugger



# Fetches an image
# if source == 'C'. then get from camera
def get_image(camera, source=None, config=None):
  if source is None:
    source = raw_input("Image source? ")

  if source == 'C':
    img = camera.capture(config)
  else:
    img = cv2.imread("images/" + source)

  return imutils.resize(img, width=1200)



# Loads the necessary config files
def prepare_config(args):
  hex_config = "config/hexagons.npy"
  camera_config = "config/camera.json"
  cv_config = args['config']

  config = CVConfig(cv_config, args['reset'], args['always_reset'])
  if not args['no_config']:
    config.load_cv_config(args["config"])

  if args['lh']:
    config.load_hex_config(hex_config)

  return config


# Automatically does a new game + update with 2 test images
def auto_test(game, camera, args):
  img1 = get_image(camera, "test_hex.png")
  img2 = get_image(camera, "test_resource.png")
  img_nums = get_image(camera, "test_nums.png")

  img3 = get_image(camera, "test_pieces1.png")
  img4 = get_image(camera, "test5/test2_4.png")

  initial = time.time()
  hexes = game.init_game(img1)
  game.new_game(img2, img_nums)

  print "Time for setup:", time.time() - initial
  Debugger.show_hexagons(img2, hexes, 0)
  Debugger.show_resources(img2, hexes, 0)

  if args['sh']:
    game.save_hexagons("config/hexagons.npy")

  initial = time.time()
  props = game.dice_rolled(1, img4)
  print "Time for pieces:", time.time() - initial
  Debugger.show_properties(img4, props, 0)


def main():
  # Parse arguments
  # -camera -r(eset) -in -out --config -ar
  parser = argparse.ArgumentParser(description='Use CV to analyze Catan board.')
  parser.add_argument('--config', nargs='?', type=str, default="config/config.json",
                     help='Config file to load/save.')
  parser.add_argument('-r', '--reset', action="store_true", default=False,
                     help='Redo configuration.')
  parser.add_argument('-ar', '--always_reset', action="store_true", default=False,
                     help='Redo configuration on each image.')
  parser.add_argument('--toss_config', action="store_true", default=False,
                     help='Throw away config i.e do not save.')
  parser.add_argument('--no_config', action="store_true", default=False,
                     help='Use the hardcoded defaults instead of loading a config file.')
  parser.add_argument('-lh', action="store_true", default=False,
                     help='Load saved hexagon configuration')
  parser.add_argument('-sh', action="store_true", default=False,
                     help='Save hexagon configuration after detection')
  args = vars(parser.parse_args())


  # Load config files
  config = prepare_config(args)
  game = CatanomousGame(config)
  auto_test(game, None, args)

  # Save config files if specified
  if not args['toss_config']:
    config.save_cv_config(args["config"])
  else:
    print "!! [CONFIG] Not saving configuration file."



if __name__ == "__main__":
  main()
