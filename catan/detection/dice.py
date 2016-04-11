import cv2
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils



class DiceDetector(object):

  def __init__(self, config):
    self._config = config

  def detect_roll(self, img):
    (h, w, z) = img.shape
    gray = cv2.cvtColor(self._img, cv2.COLOR_BGR2GRAY)
    hough_config = self._config.get("DICE_HOUGH_CIRCLE", img)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,1, h/hough_config[2],
                                param1=hough_config[0][1],
                                param2=hough_config[0][0],
                                minRadius=h/hough_config[1][0],maxRadius=h/hough_config[1][1])

    return len(circles[0])
