#!/bin/sh
# start_main.sh
# enables cv environment and launches main controller for catanomous

~/.virtualenvs/cv/bin/activate
sudo ~/.virtualenvs/cv/bin/python ~/catanomous/main.py -a
