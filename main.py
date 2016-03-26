import cv2
import imutils
import numpy as np

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
    # draw a circle enclosing the object
    ((x, y), r) = cv2.minEnclosingCircle(c)
    # cv2.circle(img, (int(x), int(y)), int(r), (0, 255, 0), 2)
    cv2.putText(img, "{}".format(res), (int(x) - 20, int(y)-30),
      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.putText(img, "{}".format(num), (int(x) - 10, int(y) + 30),
      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

def detect_image(img):
  # load the image and resize it
  orig = cv2.imread(img)
  img = imutils.resize(orig, width=1000)
  ratio = orig.shape[0] / float(img.shape[0])

  # GUIUtils.show_image(img)

  # from thresh import do_color_thresh
  # do_color_thresh(img)

  import time
  initial = time.time()

  board = BoardDetector(img)
  hexagons = board.get_hexagons()

  print "Time:", time.time() - initial

  label_hexagons(img, hexagons)
  GUIUtils.show_image(img)


def main():
  android_dir = "images/android/"
  android_imgs = ["1536x2048.jpg","2992x4000_1.jpg",
          "2992x4000_2.jpg", "2992x4000_3.jpg",
          "2992x4000_4.jpg", "3232x2416_1.jpg",
          "3232x2416_2.jpg", "3232x2416_3.jpg",
          "3232x2416_4.jpg"]
  android_test = [
          "1536x2048.jpg", "2992x4000_1.jpg",
          "2992x4000_2.jpg", "2992x4000_3.jpg",
          "3232x2416_4.jpg"
  ]

  
  
  test_dir = "images/"
  test1_imgs = [
    "test1_1.jpg",
    "test1_2.jpg",
    "test1_3.jpg",
    "test1_4.jpg",
    "test1_5.jpg",
    "test1_6.jpg",
  ]
  test2_imgs = [
    "test2_1.jpg",
    "test2_2.jpg",
  ]
  test3_imgs = [
    "test3_1.jpg",
    "test3_2.jpg",
  ]
  test4_imgs = [
    "test4_1.jpg",
    "test4_2.jpg",
    "test4_3.jpg",
  ]

  # for img in test4_imgs:
  #   print img
  #   detect_image(test_dir + img)

  # for img in android_test:
  #   print img
  #   detect_image(android_dir + img)
  
  config = CVConfig(True)
  print config.get("TEST", cv2.imread("images/test1_1.jpg"))
  print config.get("TEST", cv2.imread("images/test1_1.jpg"))
  config.save()

  
    


if __name__ == "__main__":
  main()
