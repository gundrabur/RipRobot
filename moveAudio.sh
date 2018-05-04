#!/bin/bash
echo "AUDIO RipRobot: Dateien werden auf USB-Stick verschoben"
sudo rsync --progress --modify-window=1 --update --recursive --times --ignore-existing /home/pi/RipRobot/tmp/ /media/usb/ >/home/pi/RipRobot/rsync.log
echo "AUDIO RipRobot: Dateien wurden auf USB-Stick verschoben"
