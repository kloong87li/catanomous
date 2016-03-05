import cv2
import imutils
import numpy as np

from utils.cv import CVUtils
from utils.gui import GUIUtils


class TrackbarWindow(object):

  def __init__(self):

    # Create window
    cv2.namedWindow(self.get_window_name())

    # Create trackbars 
    maxes = self.get_maxes()
    values = self.get_values()
    for key in maxes:
      cv2.createTrackbar(key, self.get_window_name(), 
                          values[key],
                          maxes[key],
                          self._callback_for(key))

  def _callback_for(self, key_name):
    return lambda v: self._value_changed(v, key_name)

  def _value_changed(self, value, name):
    self.on_value_change(value, name)
    self.show_image()

  def show_image(self):
    (img, width) = self.get_image()
    GUIUtils.update_image(imutils.resize(img, width=width), self.get_window_name())
    return

  def close_image(self):
    cv2.destroyWindow(self.get_window_name())

  # Implement these methods #
  def get_window_name(self):
    return "Window"

  def on_value_change(self, value, name):
    pass

  def get_image(self):
    return (None, None) # (image, width)

  def get_maxes(self):
    return {}

  def get_values(self):
    return {}
    






class ColorThreshTrackbar(TrackbarWindow):

  _WINDOW_NAME = 'Color Threshold'

  def __init__(self, img, replaced_color=None):
    self._replaced_color = replaced_color or [255, 255, 255]
    self._img = img
    
    # convert to hsv for color processing
    self._hsv = CVUtils.to_hsv(img)

    self._max_ranges = {
      'H_lower': 179,
      'H_upper': 179,
      'S_lower': 255,
      'S_upper': 255,
      'V_lower': 255,
      'V_upper': 255
    }

    self._bounds = {
      'H_lower': 10,
      'H_upper': 40,
      'S_lower': 100,
      'S_upper': 255,
      'V_lower': 175,
      'V_upper': 255
    }

    super(ColorThreshTrackbar, self).__init__()

  def get_window_name(self):
    return self._WINDOW_NAME

  def on_value_change(self, value, name):
    self._bounds[name] = value

  def get_image(self):
    lower = [self._bounds['H_lower'], self._bounds['S_lower'], self._bounds['V_lower']]
    upper = [self._bounds['H_upper'], self._bounds['S_upper'], self._bounds['V_upper']]
    print lower, upper
    img = CVUtils.replace_range(self._hsv, self._img, lower, upper, self._replaced_color)
    return (img, 700)

  def get_maxes(self):
    return self._max_ranges

  def get_values(self):
    return self._bounds



class GrayThreshTrackbar(TrackbarWindow):
  _WINDOW_NAME = 'Grayscale Threshold'

  def __init__(self, img, replaced_color=None):
    self._img = img
    self._gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    self._maxes = {
      'Lower': 255,
      'Upper': 255,
    }
    self._values = {
      'Lower': 10,
      'Upper': 100,
    }
    super(GrayThreshTrackbar, self).__init__()

  def get_window_name(self):
    return self._WINDOW_NAME

  def on_value_change(self, value, name):
    self._values[name] = value

  def get_image(self):
    lower = self._values['Lower']
    upper = self._values['Upper']
    mask = CVUtils.range_mask(self._gray, lower, upper)
    return (mask, 700)

  def get_maxes(self):
    return self._maxes

  def get_values(self):
    return self._values




class CannyTrackbar(TrackbarWindow):
  _WINDOW_NAME = 'Canny Threshold'

  def __init__(self, img, replaced_color=None):
    self._img = img

    self._maxes = {
      'Lower': 1024,
      'Upper': 1024,
    }
    self._values = {
      'Lower': 200,
      'Upper': 300,
    }
    super(CannyTrackbar, self).__init__()

  def get_window_name(self):
    return self._WINDOW_NAME

  def on_value_change(self, value, name):
    self._values[name] = value

  def get_image(self):
    lower = self._values['Lower']
    upper = self._values['Upper']
    print upper, lower
    edges = cv2.Canny(self._img, lower, upper)
    return (edges, 700)

  def get_maxes(self):
    return self._maxes

  def get_values(self):
    return self._values


