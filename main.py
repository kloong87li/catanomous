import cv2
import imutils
import numpy as np
from PIL import Image

import argparse, time

from utils.cv import CVUtils
from utils.gui import GUIUtils
from catan.config import CVConfig
from catan.detection.board import BoardDetector


# Labels hexagons with their resource classifications
def label_hexagons(img, hexagons):
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


def detect_image(config, img, output=None):
  # load the image and resize it
  orig = cv2.imread(img)
  catan_feature_detect(config, orig, output)
  

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

  # catan_feature_detect(config, img, output)
  GUIUtils.show_image(img)

  if output is not None:
    im = Image.fromarray(img)
    im.save(output)


def catan_feature_detect(config, img_arr, output=None):
  # Resize to make processing faster
  img = imutils.resize(img_arr, width=1000)
  # ratio = orig.shape[0] / float(img.shape[0])

  initial = time.time()

  board = BoardDetector(config, img)
  hexagons = board.get_hexagons()

  print "Time:", time.time() - initial

  label_hexagons(img, hexagons)

  if output is None:
    GUIUtils.show_image(img)
  else:
    im = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 'RGB')
    im.save(output)


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
    android_dir = "images/android/"
    android_imgs = ["1536x2048.jpg","2992x4000_1.jpg",
            "2992x4000_2.jpg", "2992x4000_3.jpg",
            "2992x4000_4.jpg", "3232x2416_1.jpg",
            "3232x2416_2.jpg", "3232x2416_3.jpg",
            "3232x2416_4.jpg"]
    android_test = [
            "1536x2048.jpg", 
            "2992x4000_1.jpg",
            # "2992x4000_2.jpg", "2992x4000_3.jpg",
            # "3232x2416_4.jpg"
    ]
    test_dir = "images/"
    test_imgs = [
      # "test1_1.png",
      # "test1_2.png",
      # "test1_3.png",
      # "test1_4.png",
      "test2_1.png",
      # "test2_2.png",
      # "test2_3.png",
      # "test3_1.png",
      # "test3_2.png",
      # "test3_3.png",
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
