#!/bin/sh
# start_main.sh
# enables cv environment and launches main controller for catanomous

. /home/pi/.virtualenvs/cv/bin/activate
sudo /home/pi/.virtualenvs/cv/bin/python /home/pi/catanomous/main.py -a
