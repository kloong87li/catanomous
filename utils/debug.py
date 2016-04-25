import cv2
import imutils
import numpy as np
from PIL import Image

from utils.cv import CVUtils
from utils.gui import GUIUtils


class Debugger(object):

  # Labels detected hexagons with their resource classifications
  @staticmethod
  def show_hexagons(img, hexagons, ui_delay=250):
    for i in xrange(len(hexagons)):
      c = hexagons[i]._contour

      # draw contour
      cv2.drawContours(img, [c], -1, (0, 255, 0), 2)

    GUIUtils.update_image(img)
    cv2.waitKey(ui_delay)

  @staticmethod
  def show_resources(img, hexagons, ui_delay=250):
    for i in xrange(len(hexagons)):
      c = hexagons[i]._contour
      res = hexagons[i]._resource
      num = hexagons[i]._number
      ((x, y), r) = cv2.minEnclosingCircle(c)
      
      cv2.putText(img, "{}".format(res), (int(x) - 20, int(y)-30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
      cv2.putText(img, "{}".format(num), (int(x) - 10, int(y) + 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    GUIUtils.update_image(img)
    cv2.waitKey(ui_delay)

  # Displays the detected property locations on an image
  @staticmethod
  def show_properties(img, properties, ui_delay=250):
    for (tile, prop_list) in properties:
      for (pt, c) in prop_list:
        (x,y) = pt
        color = (0, 0, 255) if c.isupper() else (0, 255, 0)
        cv2.circle(img, tuple(pt), 25, color, 1)

        print tile._resource, tile._number, prop_list
      
    GUIUtils.update_image(img)
    cv2.waitKey(ui_delay)
    return 

