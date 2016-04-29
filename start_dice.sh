#!/bin/sh
# start_dice.sh
# enables cv environment and launches dice controller for catanomous

export PYTHONPATH=${PYTHONPATH}:/usr/local/lib/python2.7/site-packages
. /home/.virtualenvs/cv/bin/activate
sudo /home/.virtualenvs/cv/bin/python /home/catanomous/dice_main.py -a
