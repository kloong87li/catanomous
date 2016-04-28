import cv2
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils



class DiceDetector(object):

  def __init__(self, config):
    self._config = config

  def detect_roll(self, img):
    (h, w, z) = img.shape
    (lower, upper) = self._config.get("DICE_RED_MASK", img)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    red_mask = CVUtils.range_mask(hsv, lower, upper)
    red_only = CVUtils.mask_image(img, red_mask)

    gray = cv2.cvtColor(red_only, cv2.COLOR_BGR2GRAY)
    hough_config = self._config.get("DICE_HOUGH_CIRCLE", red_only)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1, h/hough_config[2],
                                param1=hough_config[0][1],
                                param2=hough_config[0][0],
                                minRadius=h/hough_config[1][0],maxRadius=h/hough_config[1][1])

    if circles is None:
      return 0
    return len(circles[0])
