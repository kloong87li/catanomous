import cv2
import numpy as np
import imutils

from utils.cv import CVUtils
from utils.gui import GUIUtils

from PIL import Image
import pytesseract


class TileNumDetector(object):

  _VALID_NUMS = ['2', '3', '4', '5', '6', '8', '9', '10', '11', '12']

  def __init__(self, img):
    pass

  def detect_number(self, img, mask, circle, erosion=0):
    num = self._attempt_detection(img, np.copy(mask), circle, erosion)
    while (num not in self._VALID_NUMS and erosion <= 2):
      erosion = erosion + 1
      num = self._attempt_detection(img, np.copy(mask), circle, erosion)

    if num not in self._VALID_NUMS:
      return None
    else:
      return num


  def _attempt_detection(self, img, mask, circle, erosion=2):
    # Isolate number by thresholding
    img = CVUtils.replace_color(img, CVUtils.invert_mask(mask), [255,255,255])
    if erosion > 0:
      img = cv2.erode(img, np.ones((erosion, erosion), np.uint8))
    img = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 125, 255, cv2.THRESH_BINARY)[1]

    # Only retain large enough contours
    # img = cv2.bilateralFilter(img , 3, 50, 50)
    contours = cv2.findContours(CVUtils.invert_mask(img), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
    lcontours = []

    for c in contours:
      x, y, w, h = cv2.boundingRect(c)
      if h > circle[2]/3: # if larger than a 3rd of the circle radius
        lcontours.append(c)

    # Draw numbers only onto empty image
    mask.fill(255)
    img = mask
    cv2.drawContours(img, lcontours, -1, (0,0,0), -1)

    # Preprocess for tesseract OCR
    img = imutils.resize(img, width=400)

    GUIUtils.show_image(img)


    cv2.imwrite( "./images/test.jpg", img);
    pil_image = Image.fromarray(img)
    return pytesseract.image_to_string(pil_image, config="-psm 7 digits")


