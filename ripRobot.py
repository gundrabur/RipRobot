#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import time
import pygame
import datetime
import argparse
import RPi.GPIO as GPIO
import threading

RIPITDIRTEMPLATE = "'\"/$artist/$album\"'"
VERSION = "1.03de"

class RipRobot():

    def __init__(self,cdDrive,outputPath,timeout):
        self.cdDrive = cdDrive
        self.outputPath = outputPath
        self.timeout = timeout
        self.cdDrive.init()
    
    def initLED(self):
        # Warnungen ausschalten
        GPIO.setwarnings(False)
        # RPi.GPIO Layout verwenden (wie Pin-Nummern)
        GPIO.setmode(GPIO.BOARD)
        # Pin 13 (GPIO 27) auf Output setzen
        GPIO.setup(13, GPIO.OUT)
        # Pin 15 (GPIO 22) auf Output setzen
        GPIO.setup(15, GPIO.OUT)

        # LEDs einschalten
        self.allLED(1)
        time.sleep(1)
        # LEDs ausschalten
        self.allLED(0)
    
    def allLED(self,state):
        self.redLED(state)
        self.greenLED(state)

    def redLED(self,state):
        GPIO.output(13,state)

    def greenLED(self,state):
        GPIO.output(15,state)

    def start(self):
        #open the cd drawer
        subprocess.call(["eject"])
        print "AUDIO RipRobot: Bitte CD einlegen ..."
        #loop until a disk hasnt been inserted within the timeout
        lastTimeDiskFound = time.time()
        while (lastTimeDiskFound + self.timeout) > time.time():
            #is there a disk in the drive?
            if self.cdDrive.get_empty() == False:
                # Disk found
                # is it an audio cd?
                if self.cdDrive.get_track_audio(0) == True:
                    print "AUDIO RipRobot: Audio CD gefunden! Ripping startet"
                    self.redLED(0)
                    self.greenLED(1)
                    #run ripit
                    # getting subprocess to run ripit was difficult
                    #  due to the quotes in the --dirtemplate option
                    #   this works though!
                    ripit = subprocess.Popen("ripit --transfer http --coder 2 --outputdir " + self.outputPath + " --dirtemplate=" + RIPITDIRTEMPLATE + " --nointeraction", shell=True)
                    ripit.communicate()
                    # rip complete
                    # move to USB
                    # wait for a bit
                    print "AUDIO RipRobot: Ripping beendet!"
                    self.redLED(1)
                    self.greenLED(1)
                    # move files to USB using a shell script
                    subprocess.call("/home/pi/RipRobot/moveAudio.sh")
                    print "AUDIO RipRobot: CD wird ausgeworfen"
                    # use eject command rather than pygame.cd.eject as I had problems with my drive
                    subprocess.call(["eject"])
                    self.redLED(0)
                    self.greenLED(1)
                    lastTimeDiskFound = time.time()
                else:
                    print "AUDIO RipRobot: Die eingelegte CD ist keine Audio CD!"
                    subprocess.call(["eject"])
                    self.redLED(1)
                    self.greenLED(0)
                lastTimeDiskFound = time.time()
                print "AUDIO RipRobot: Warten auf neue CD ..."
            else:
                # No disk - eject the tray
                subprocess.call(["eject"])
                self.greenLED(1)
                self.redLED(0)
            # wait for a bit, before checking if there is a disk
            time.sleep(5)

        # timed out, a disk wasnt inserted
        subprocess.call("/home/pi/RipRobot/cleanAudio.sh")
        print "AUDIO RipRobot: Wartezeit zu lang, System wird abgeschaltet!"
        self.redLED(1)
        self.greenLED(0)
        # close the drawer
        subprocess.call(["eject", "-t"])
        #finished - cleanup
        self.cdDrive.quit()

if __name__ == "__main__":

    print ""
    print "############################################"
    print "##     Willkommen zum AUDIO RipRobot      ##"
    print "##           Version: " + VERSION + "              ##"
    print "## AUDIO RipRobot basiert auf Code von:   ##"
    print "##           StuffAboutCode.com           ##"
    print "## Freie Software Creativ Commmon License ##"
    print "############################################"
    print ""

    #Command line options
    parser = argparse.ArgumentParser(description="AUDIO RipRobot")
    parser.add_argument("outputPath", help="The location to rip the CD to")
    parser.add_argument("timeout", help="The number of seconds to wait for the next CD")
    args = parser.parse_args()

    #Initialize the CDROM device
    pygame.cdrom.init()

    # make sure we can find a drive
    if pygame.cdrom.get_count() == 0:
        print "AUDIO RipRobot: Kein CD-Laufwerk gefunden!"
    elif pygame.cdrom.get_count() > 1:
        print "AUDIO RipRobot: Mehr als ein CD-Laufwerk gefunden! Das wird nicht unterstützt, bitte nur ein CD-Laufwerk anschließen!"
    elif pygame.cdrom.get_count() == 1:
        print "AUDIO RipRobot: CD-Laufwerk gefunden! Es geht los!"
        print int(args.timeout)
        RipRobot = RipRobot(pygame.cdrom.CD(0),args.outputPath,int(args.timeout))
        RipRobot.initLED()
        RipRobot.start()

    #clean up
    RipRobot.allLED(0)
    GPIO.cleanup()
    pygame.cdrom.quit()
