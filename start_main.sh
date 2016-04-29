#!/bin/sh
# start_main.sh
# enables cv environment and launches main controller for catanomous

export PYTHONPATH=${PYTHONPATH}:/usr/local/lib/python2.7/site-packages
. /home/pi/.virtualenvs/cv/bin/activate
cd /home/pi/catanomous
sudo /home/pi/.virtualenvs/cv/bin/python main.py -a
