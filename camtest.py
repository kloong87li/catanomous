from utils.camera import Camera
from catan.config import CVConfig

from utils.gui import GUIUtils
from utils.cv import CVUtils

import cv2
import imutils



def process_token(token, camera):
  if token == 'AWB':
    val1 = raw_input("Val1: ")
    val2 = raw_input("Val2: ")
    camera.set_setting(token, (float(val1), float(val2)))
  elif token == 'ZOOM':
    print "Not supported yet."
  elif token == 'RESOLUTION':
    val1 = raw_input("W: ")
    val2 = raw_input("H: ")
    camera.set_setting(token, (int(val1), int(val2)))
  else:
    value = raw_input("New value: ")
    camera.set_setting(token, int(value))

def get_picture(camera, config=None):
  img = camera.capture(config)
  GUIUtils.update_image(imutils.resize(img, width=1200))
  cv2.waitKey(100)
  return img

def main():
  cam_config = "config/camera.json"
  config = CVConfig("config/config.json")
  config.load_cam_config(cam_config)

  camera = Camera(config)
  config_json = None

  try:
    camera.start()

    while (True):
      print "Enter a camera setting to change. (or 'P' to preview, 'X' to quit, 'V' to see current settings, 'S' to save image, 'L' to load config, 'SC' to save config)"
      print "1 to save hexagon pic, 2 to save resource pic"
      token = raw_input("Input: ")

      if token == 'P':
        get_picture(camera)
      elif token == 'X':
        print "Saving config as:", cam_config
        config.save_cam_config(cam_config)
        break
      elif token == 'SC':
        print "Saving config as:", cam_config
        config.save_cam_config(cam_config)
      elif token == 'V':
        settings = config.get_cam_all()
        print "Settings for: ", cam_config
        for key in settings:
          print key, ": ", settings[key]
      elif token == 'S':
        img = get_picture(camera)
        path = raw_input("Path: ")
        CVUtils.save_img(img, path)
      elif token == 'L':
        cam_config = raw_input('Config path:')
        config_json = CVConfig.load_json(cam_config)
        camera._set_config(config_json)
        get_picture(camera)
      elif token =='1':
        img = get_picture(camera, CVConfig.load_json("config/camera_hex.json"))
        CVUtils.save_img(img, "images/test_hex.png")
      elif token =='2':
        img = get_picture(camera)
        CVUtils.save_img(img, "images/test_resource.png")
      else:
        process_token(token, camera)
        get_picture(camera)

  finally:
    camera.stop()



if __name__ == "__main__":
  main()
