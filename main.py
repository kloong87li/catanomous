import cv2
import imutils
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

from catan.detection.board import BoardDetector


# Labels hexagons with their resource classifications
def label_hexagons(img, hexagons):
  for i in xrange(len(hexagons)):
    c = hexagons[i]._contour
    res = hexagons[i]._resource
    # draw a circle enclosing the object
    ((x, y), r) = cv2.minEnclosingCircle(c)
    # cv2.circle(img, (int(x), int(y)), int(r), (0, 255, 0), 2)
    cv2.putText(img, "{}".format(res), (int(x) - 10, int(y)),
    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

def detect_image(img):
  # load the image and resize it
  orig = cv2.imread(img)
  img = imutils.resize(orig, width=1000)
  ratio = orig.shape[0] / float(img.shape[0])

  # GUIUtils.show_image(img)

  # from thresh import do_color_thresh
  # do_color_thresh(img)

  board = BoardDetector(img)
  hexagons = board.get_hexagons()

  label_hexagons(img, hexagons)
  GUIUtils.show_image(img)


def main():
  imgs = ["1536x2048.jpg","2992x4000_1.jpg",
          "2992x4000_2.jpg", "2992x4000_3.jpg",
          "2992x4000_4.jpg", "3232x2416_1.jpg",
          "3232x2416_2.jpg", "3232x2416_3.jpg",
          "3232x2416_4.jpg"]

  test_imgs = [
    "1536x2048.jpg","2992x4000_1.jpg","2992x4000_2.jpg"
  ]
  for img in test_imgs:
    print img
    detect_image("images/" + img)

  

  
    


if __name__ == "__main__":
  main()
