#!/bin/bash
uptime
echo "AUDIO RipRobot: Temporäre Dateien werden gelöscht"
sudo rm -r /home/pi/RipRobot/tmp/*
echo "AUDIO RipRobot: USB-Stick wird sicher ausgeworfen"
df
sudo umount /dev/sda1
df
echo "AUDIO RipRobot: Programm wird beenden"
sudo shutdown
