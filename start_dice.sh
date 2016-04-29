#!/bin/sh
# start_dice.sh
# enables cv environment and launches dice controller for catanomous

export PYTHONPATH=${PYTHONPATH}:/usr/local/lib/python2.7/site-packages
. /home/.virtualenvs/cv/bin/activate
cd /home/pi/catanomous
sudo /home/.virtualenvs/cv/bin/python dice_main.py -a
