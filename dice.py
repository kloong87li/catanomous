import cv2
import imutils
import numpy as np
from PIL import Image

import argparse, time

from utils.cv import CVUtils
from utils.gui import GUIUtils
from catan.config import CVConfig
from catan.detection.dice import DiceDetector


def detect_image(config, img, output=None):
  # load the image and resize it
  orig = cv2.imread(img)
  catan_dice_detect(config, orig, output)
  

def detect_image_raspi(config, output=None):
  from picamera.array import PiRGBArray
  from picamera import PiCamera

  # initialize the camera and grab a reference to the raw camera capture
  camera = PiCamera()
  rawCapture = PiRGBArray(camera)
   
  # allow the camera to warmup
  time.sleep(0.1)

  camera.resolution = (1280, 720)
  camera.framerate = 30
  # Wait for the automatic gain control to settle
  time.sleep(2)
  # Now fix the values
  camera.shutter_speed = camera.exposure_speed
  camera.exposure_mode = 'off'
  g = camera.awb_gains
  camera.awb_mode = 'off'
  camera.awb_gains = g
   
  # grab an image from the camera
  camera.capture(rawCapture, format="bgr")
  img = rawCapture.array

  # catan_dice_detect(config, img, output)
  GUIUtils.show_image(img)

  if output is not None:
    im = Image.fromarray(img)
    im.save(output)


def catan_dice_detect(config, img, output):
  detector = DiceDetector(config, img)
  num = detector.detect_roll()
  print "Detected roll of:", num

def main():
  # Parse arguments
  # -camera -r(eset) -in -out --config -ar
  parser = argparse.ArgumentParser(description='Use CV to analyze Catan board.')
  parser.add_argument('-in', nargs='?', type=str,
                     help='Input image to analyze. If not specified, will run hardcoded test images.')
  parser.add_argument('-out', nargs='?', type=str,
                     help='Output image. If not specified, will display result in GUI.')
  parser.add_argument('--config', nargs='?', type=str, default="config.json",
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
  args = vars(parser.parse_args())

  # Initialize config
  config = CVConfig(args['config'], args['reset'], args['always_reset'], args['no_config'])

  # Use camera if specified
  if args['camera']:
    # Implement later for raspi
    detect_image_raspi(config, args['out'])
    return

  # Otherwise use fixed images
  if args['in']:
    print args['in']
    detect_image(config, args['in'], args['out'])
  else:
    test_dir = "images/"
    test_imgs = [
      "dice.png"
    ]

    for img in test_imgs:
      detect_image(config, test_dir + img)


  # Save config
  if not args['toss_config']:
    config.save()
  else:
    print "!! [CONFIG] Not saving configuration file."




if __name__ == "__main__":
  main()
