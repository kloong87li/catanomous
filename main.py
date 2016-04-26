import argparse, time
from catan.main_controller import MainController

def main():
  # Parse arguments
  # -camera -r(eset) -in -out --config -ar
  parser = argparse.ArgumentParser(description='Use CV to analyze Catan board.')
  parser.add_argument('-t', '--test', action="store_true", default=False,
                     help='Run test.')
  parser.add_argument('-rh', '--reset_hex', action="store_true", default=False,
                     help='Reset Hexagons.')
  parser.add_argument('-sr', '--skip_resources', action="store_true", default=False,
                     help='Skip resource detection during test.')
  args = vars(parser.parse_args())


  controller = MainController()
 
  if args['test']:
    controller.start_test(args['reset_hex'], args['skip_resources'])
  else:
    controller.start()

if __name__ == "__main__":
  main()
