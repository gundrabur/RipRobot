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
       
        # CD Schublade öffnen
        self.LEDGreenBlink(True,2000) # grüne LED an
        subprocess.call(["eject"])
        print "AUDIO RipRobot: 30 Sekunden warten, bis die Echtzeituhr gestellt wurde"
        time.sleep(30)
        print "AUDIO RipRobot: Bitte CD einlegen ..."
        # Diese Schleife läuft so lange, bis nach Ablauf des Timeouts keine CD eingelegt wurde
        lastTimeDiskFound = time.time()
        while (lastTimeDiskFound + self.timeout) > time.time():
            # Ist eine CD im Laufwerk?
            if self.cdDrive.get_empty() == False:
                # Ja, CD gefunden!
                # Ist es auch eine Audio-CD?
                if self.cdDrive.get_track_audio(0) == True:
                    print "AUDIO RipRobot: Audio CD gefunden! Ripping startet"
                    # ripit starten
                    # LEDs bedeuten: langsam blinken = Rippen läuft!
                    # grün blinkt langsam, rot aus
                    self.LEDGreenBlink(True,2)
                    # rot aus
                    self.LEDRedBlink(False,1)
                    # Hier startet der eigentlich Rip-Prozess. Dazu wird das Tool "RipIt" gestartet
                    ripit = subprocess.Popen("ripit --transfer http --coder 2 --outputdir " + self.outputPath + " --dirtemplate=" + RIPITDIRTEMPLATE + " --nointeraction", shell=True)
                    ripit.communicate()
                    # RipIt ist fertig
                    # Jetzt die Daten auf den USB-Stick kopieren
                    print "AUDIO RipRobot: Ripping beendet!"
                    # ganz schnelles Blinken = Daten werden auf USB-Stick verschoben
                    self.LEDGreenBlink(True,8)
                    # Shell-Script starten
                    subprocess.call("/home/pi/RipRobot/moveAudio.sh")
                    print "AUDIO RipRobot: CD wird ausgeworfen"
                    # CD auswerfen
                    subprocess.call(["eject"])
                    # Grüne LED an
                    self.LEDGreenBlink(True,2000)
                    # rotes Blinken aus!
                    self.LEDRedBlink(False,1)
                    lastTimeDiskFound = time.time()
                else:
                    # das ging schief, die CD hat einen Fehler oder ist keine Audio-CD
                    print "AUDIO RipRobot: Die eingelegte CD ist keine Audio CD!"
                    subprocess.call(["eject"])
                    # Grün an, damit der Benutzer weiß: "Audio-CD einlegen"
                    self.LEDGreenBlink(True,2000)
                    # Rot blinkt = Fehler
                    self.LEDRedBlink(True,4)
                lastTimeDiskFound = time.time()
                print "AUDIO RipRobot: Warten auf neue CD ..."
            else:
                # Keine CD im Laufwerk, also auswerfen
                subprocess.call(["eject"])
            # 10 Sekunden warten, bis eine neue Abfrage nach einer CD erfolgt
            print "AUDIO RipRobot: Warten auf neue CD ..."
            time.sleep(10)

        # Timeout abgelaufen, AUDIO RipRobot herunterfahren
        # hier wird ein Shellscript aufgerufen, dass das temporäre Verzeichnis leert
        # und den Raspi abschaltet
        subprocess.call("/home/pi/RipRobot/cleanAudio.sh")
        print "AUDIO RipRobot: Wartezeit zu lang, System wird abgeschaltet!"
        # grün aus
        self.LEDGreenBlink(False,2)
        # schnell blinken = Fehler
        self.LEDRedBlink(True,4)
        # CD-Laufwerk schließen
        subprocess.call(["eject", "-t"])
        # Ende, runterfahren!
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

    # Kommandozeile auslesen
    parser = argparse.ArgumentParser(description="AUDIO RipRobot")
    parser.add_argument("outputPath", help="The location to rip the CD to")
    parser.add_argument("timeout", help="The number of seconds to wait for the next CD")
    args = parser.parse_args()

    # CD-Laufwerk initialisieren
    pygame.cdrom.init()

    # Gibt es überhaupt ein CD-Laufwerk?
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
