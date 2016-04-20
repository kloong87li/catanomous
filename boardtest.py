import cv2
import imutils
import numpy as np
from PIL import Image

import argparse, time

from utils.cv import CVUtils
from utils.gui import GUIUtils
from catan.config import CVConfig
from catan.game import CatanomousGame


# Labels detected hexagons with their resource classifications
def show_new_game(img, hexagons, delay=250):
  for i in xrange(len(hexagons)):
    c = hexagons[i]._contour
    res = hexagons[i]._resource
    num = hexagons[i]._number
    ((x, y), r) = cv2.minEnclosingCircle(c)
    
    # draw contour
    cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
    
    cv2.putText(img, "{}".format(res), (int(x) - 20, int(y)-30),
      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.putText(img, "{}".format(num), (int(x) - 10, int(y) + 30),
      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

  GUIUtils.update_image(img)
  cv2.waitKey(delay)


# Displays the detected property locations on an image
def show_properties(img, properties, delay=250):
  for (tile, prop_list) in properties:
    for (pt, c) in prop_list:
      (x,y) = pt
      cv2.circle(img, tuple(pt), 25, (0, 255, 0), 1)
    
  GUIUtils.update_image(img)
  cv2.waitKey(delay)
  return 


# Fetches an image
# if source == 'C'. then get from camera
def get_image(camera, source=None, config=None):
  if source is None:
    source = raw_input("Image source? ")

  if source == 'C':
    img = camera.capture()
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

  if args['camera']:
    config.load_cam_config("config/camera.json")

  if args['lh']:
    config.load_hex_config(hex_config)

  return config


# Processes each user input
def handle_command(cmd, game, camera, args):
  if cmd == 'N':
    hexes = get_image(camera, None, CVConfig.load_json("config/camera_hex.json"))
    resources = get_image(camera)
    numbers = get_image(camera)

    initial = time.time()
    hexes = game.new_game(hexes)
    game.setup_resources(resources, numbers)
    print "Time:", time.time() - initial
    show_new_game(resources, hexes)

    if args['sh']:
      game.save_hexagons("config/hexagons.npy")

  elif cmd == 'U':
    img = get_image(camera)
    props = game.update_properties(img)
    show_properties(img, props)

  elif cmd == 'D':
    img = get_image(camera)
    game.dice_rolled(img)


# Automatically does a new game + update with 2 test images
def auto_test(game, camera, args):
  img1 = get_image(camera, "test1_hex.png")
  img2 = get_image(camera, "test1_color.png")
  img3 = get_image(camera, "test1_pieces.png")

  initial = time.time()
  hexes = game.new_game(img1)
  game.setup_resources(img2, img2)

  print "Time:", time.time() - initial
  show_new_game(img2, hexes, 0)

  if args['sh']:
    game.save_hexagons("config/hexagons.npy")

  props = game.update_properties(img3)
  show_properties(img3, props, 0)


def main():
  # Parse arguments
  # -camera -r(eset) -in -out --config -ar
  parser = argparse.ArgumentParser(description='Use CV to analyze Catan board.')
  parser.add_argument('--config', nargs='?', type=str, default="config/config.json",
                     help='Config file to load/save.')
  parser.add_argument('--camera', '-c', action="store_true", default=False,
                     help='Whether or not to use Raspi camera.')
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
  parser.add_argument('-a', action="store_true", default=False,
                     help='Automatically run test')
  args = vars(parser.parse_args())


  # Load config files
  config = prepare_config(args)

  # Initialize camera if necessary
  use_camera = args['camera']
  camera = None
  if use_camera:
    from utils.camera import Camera
    camera = Camera(config)
    camera.start()

  game = CatanomousGame(config)
  if args['a']:
    auto_test(game, camera, args)
  else: # Main command loop
    while (True):
      print "'N' for new game, 'U' to update game state, 'D' for dice roll, X' to quit."
      command = raw_input("Command: ")

      if command == 'X':
        break
      else:
        handle_command(command, game, camera, args)

  # Close camera if necessary
  if use_camera and camera is not None:
    camera.stop()

  # Save config files if specified
  if not args['toss_config']:
    config.save_cv_config(args["config"])
  else:
    print "!! [CONFIG] Not saving configuration file."



if __name__ == "__main__":
  main()
