import cv2
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils

from PIL import Image
import pytesseract


class TileNumDetector(object):

  def __init__(self, img):
    pass

  def detect_number(self):
    img = self._get_roi(self._hex_img)

    # # Blur and get circles
    # gray = cv2.cvtColor(cv2.medianBlur(img, 5), cv2.COLOR_BGR2GRAY)
    # (h, w) = gray.shape
    # circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1, w/2,
    #                             param1=50,param2=30,minRadius=w/10,maxRadius=w/2)
    # if circles is None:
    #   return

    # # Isolate circle
    # # TODO assert only one circle found
    # circle = np.uint8(np.around(circles))[0, :][0]
    # mask = np.zeros((h, w), np.uint8)
    # # Draw mask, shrink radius to decrease shadow effects
    # cv2.circle(mask, (circle[0], circle[1]), np.uint8(circle[2]*.75), (255, 255, 255), thickness=-1)

    # Isolate number by thresholding
    img = CVUtils.mask_image(img, mask)
    img = CVUtils.replace_color(img, CVUtils.invert_mask(mask), [255,255,255])
    img = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 120, 255, cv2.THRESH_BINARY)[1]

    # Only retain large enough contours
    img = cv2.erode(img, np.ones((2, 2), np.uint8))
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
    img = cv2.dilate(img, np.ones((1,2), np.uint8))
    img = imutils.resize(img, width=500)

    GUIUtils.show_image(img)
    cv2.imwrite( "./images/test.jpg", img);
    pil_image = Image.fromarray(img)
    print(pytesseract.image_to_string(pil_image, config="-psm 7 digits"))


