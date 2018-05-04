#!/bin/bash
echo "AUDIO AutoRipper: Temporäre Dateien werden gelöscht"
sudo rm -r /home/pi/AutoRipper/tmp/*
sudo umount /dev/sda1
df
#sudo shutdown
