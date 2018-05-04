#!/bin/bash
echo "AUDIO RipRobot: Alle Temporäre Dateien werden vor dem Start gelöscht"
sudo rm -r /home/pi/RipRobot/tmp/*
cd /home/pi/RipRobot
python ripRobot.py /home/pi/RipRobot/tmp 180
echo "AUDIO RipRobot: System wird abgeschaltet!"
