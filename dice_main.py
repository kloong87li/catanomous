import argparse, time
from catan.dice_controller import DiceController

def main():
  # Parse arguments
  parser = argparse.ArgumentParser(description='Use CV to analyze Catan board.')
  parser.add_argument('-t', '--test', action="store_true", default=False,
                     help='Run test.')
  args = vars(parser.parse_args())


  controller = DiceController()
 
  if args['test']:
    controller.start_test()
  else:
    controller.start()

if __name__ == "__main__":
  main()
