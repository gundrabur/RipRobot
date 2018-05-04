#!/bin/bash
echo "AUDIO AutoRipper: Dateien werden auf USB-Stick verschoben"
sudo rsync --progress --modify-window=1 --update --recursive --times --ignore-existing /home/pi/AutoRipper/tmp/ /media/usb/ >/home/pi/AutoRipper/rsync.log
#sudo rm -r /home/pi/AutoRipper/tmp/*
echo "AUDIO AutoRipper: Dateien wurden auf USB-Stick verschoben"
