import cv2
import imutils
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

from catan.board import BoardDetector



def main():
  test_img = "images/1536x2048.jpg"

  # load the image and resize it
  orig = cv2.imread(test_img)
  img = imutils.resize(orig, width=1000)
  ratio = orig.shape[0] / float(img.shape[0])

  GUIUtils.show_image(img)

  board = BoardDetector(img)
  hexagons = board.get_hexagons()

  for i in xrange(len(hexagons)):
    c = hexagons[i]._contour
    # draw a circle enclosing the object
    ((x, y), r) = cv2.minEnclosingCircle(c)
    cv2.circle(img, (int(x), int(y)), int(r), (0, 255, 0), 2)
    cv2.putText(img, "#{}".format(i), (int(x) - 10, int(y)),
      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

  GUIUtils.show_image(img)

  
  
  


if __name__ == "__main__":
  main()
