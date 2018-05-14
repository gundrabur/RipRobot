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
VERSION = "1.04de"

class RipRobot():

    def __init__(self,cdDrive,outputPath,timeout):
        self.cdDrive = cdDrive
        self.outputPath = outputPath
        self.timeout = timeout
        self.cdDrive.init()
        
        # GPIO initialisieren
        # Warnungen ausschalten
        GPIO.setwarnings(False)
        
        # RPi.GPIO Layout verwenden (wie Pin-Nummern)
        GPIO.setmode(GPIO.BOARD)
        
        # Pin 12 (GPIO 18) auf PWM setzen, grüne LED, kann blinken per PWM!
        GPIO.setup(12, GPIO.OUT)

        # Pin 13 (GPIO 33) auf PWM setzen, rote LED, kann blinken per PWM!
        GPIO.setup(33, GPIO.OUT)

        # das ist die Variable, über die die blinkende LED gesteuert wird
        self.LED_green = GPIO.PWM(12, 4)

        # das ist die Variable, über die die blinkende LED gesteuert wird
        self.LED_red = GPIO.PWM(33, 4)

    def allLED(self,state):
        self.LEDGreenBlink(state,2)
        self.LEDRedBlink(state,2)

    def LEDGreenBlink(self,state,speed):
        if state == True:
            self.LED_green.start(50) # 50% An/Aus-Verhältnis
            self.LED_green.ChangeFrequency(speed)
        else:
            self.LED_green.stop()

    def LEDRedBlink(self,state,speed):
        if state == True:
            self.LED_red.start(50) # 50% An/Aus-Verhältnis
            self.LED_red.ChangeFrequency(speed)
        else:
            self.LED_red.stop()

    def start(self):
        
        # LEDs einschalten
        self.allLED(True)
        # zwei Sekunden warten
        time.sleep(2)
        # LEDs ausschalten
        self.allLED(False)
       
        #open the cd drawer
        self.LEDGreenBlink(True,2000) #####>#####
        subprocess.call(["eject"])
        print "AUDIO RipRobot: 30 Sekunden warten, bis die Echtzeituhr gestellt wurde"
        time.sleep(30)
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
                    #run ripit
                    # getting subprocess to run ripit was difficult
                    # due to the quotes in the --dirtemplate option
                    # this works though!
                    
                    # langsam blinken = Rippen läuft!
                    # grün blinkt langsam, aus
                    self.LEDGreenBlink(True,2) #####>#####
                    # rot aus
                    self.LEDRedBlink(False,1) #####>#####

                    ripit = subprocess.Popen("ripit --transfer http --coder 2 --outputdir " + self.outputPath + " --dirtemplate=" + RIPITDIRTEMPLATE + " --nointeraction", shell=True)
                    ripit.communicate()
                    # rip complete
                    # move to USB
                    # wait for a bit
                    print "AUDIO RipRobot: Ripping beendet!"
                    
                    # ganz schnelles Blinken = Daten werden auf USB-Stick verschoben
                    self.LEDGreenBlink(True,8)  #####>#####
                    
                    # move files to USB using a shell script
                    subprocess.call("/home/pi/RipRobot/moveAudio.sh")
                    print "AUDIO RipRobot: CD wird ausgeworfen"
                    # use eject command rather than pygame.cd.eject as I had problems with my drive
                    subprocess.call(["eject"])
                    
                    # Grün an
                    self.LEDGreenBlink(True,2000)  #####>#####
                    # rotes Blinken aus!
                    self.LEDRedBlink(False,1)
                    
                    lastTimeDiskFound = time.time()
                else:
                    print "AUDIO RipRobot: Die eingelegte CD ist keine Audio CD!"
                    subprocess.call(["eject"])
 
                    # Grün an, damit der Benutzer weiß: "Audio-CD einlegen"
                    self.LEDGreenBlink(True,2000)  #####>#####
                    # schnell blinken = Fehler
                    self.LEDRedBlink(True,4) #####>#####
                
                lastTimeDiskFound = time.time()
                print "AUDIO RipRobot: Warten auf neue CD ..."
            else:
                # No disk - eject the tray
                subprocess.call(["eject"])
                # wait for a bit, before checking if there is a disk
            print "AUDIO RipRobot: Warten auf neue CD ..."
            time.sleep(10)

        # timed out, a disk wasnt inserted
        subprocess.call("/home/pi/RipRobot/cleanAudio.sh")
        print "AUDIO RipRobot: Wartezeit zu lang, System wird abgeschaltet!"
        
        # grün aus
        self.LEDGreenBlink(False,2)  #####>#####
        # schnell blinken = Fehler
        self.LEDRedBlink(True,4) #####>#####
        
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
        print "AUDIO RipRobot: Timeout steht auf " + args.timeout + " Sekunden"
        RipRobot = RipRobot(pygame.cdrom.CD(0),args.outputPath,int(args.timeout))
        RipRobot.start()

    #clean up
    GPIO.cleanup()
    pygame.cdrom.quit()
