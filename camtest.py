from utils.camera import Camera
from catan.config import CVConfig

from utils.gui import GUIUtils


def process_token(token, camera):
  if token == 'AWB':
    val1 = raw_input("Val1: ")
    val2 = raw_input("Val2: ")
    camera.set_setting(token, (float(val1), float(val2)))
  elif token == 'Zoom':
    print "Not supported yet."
  elif token == 'Resolution':
    print "Not supported yet."
  else:
    value = raw_input("New value: ")
    camera.set_setting(token, int(value))


def main():
  config = CVConfig("config/config.json")
  camera = Camera(config, "config/camera.json")

  try:
    camera.start()

    while (True):
      print "Enter a camera setting to change. (or 'P' to preview, 'X' to quit, 'V' to see current settings)"
      token = raw_input("Input: ")

      if token == 'P':
        img = camera.capture()
        GUIUtils.show_image(img)
      elif token == 'X':
        break
      elif token == 'V':
        settings = config.get_cam_all()
        for key in settings:
          print key, ": ", settings[key]
      else:
        process_token(token, camera)


  finally:
    camera.stop()



if __name__ == "__main__":
  main()