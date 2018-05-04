#!/bin/bash
echo "AUDIO RipRobot: Temporäre Dateien werden gelöscht"
sudo rm -r /home/pi/RipRobot/tmp/*
sudo umount /dev/sda1
df
sudo shutdown
