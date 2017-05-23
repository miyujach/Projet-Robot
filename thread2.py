from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import multiprocessing

import RPi.GPIO as GPIO
import time
import threading


moveSleepDelay = 0.1
moveSteps = 10

actionGauche = 7
actionDroite = 5
actionAvancer = 3
actionAttraperRelacher = 11
pinCamGauche = 15
pinCamDroite = 13
headMoveDirection = True # True = Gauche, False = Droite

pill2kill = threading.Event()

#Resolution camera
resolutionX = 320
resolutionY = 240

#Load a cascade file for detecting faces
face_cascade = cv2.CascadeClassifier('/home/pi/opencv_regular/opencv-3.2.0/data/haarcascades/haarcascade_frontalface_alt.xml')

camera = PiCamera()
camera.resolution = (resolutionX, resolutionY)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=camera.resolution )
# allow the camera to warmup
time.sleep(0.1)

#init la position du carre a 0
cx = 0
cy = 0
positions = ''
font = cv2.FONT_HERSHEY_SIMPLEX
center = []


def actionRoues(pin):
	if pin == 200 and oldPin != 200:
		#Eteind la led	
		GPIO.setup(oldPin,GPIO.OUT)
		print "LED off"
		GPIO.output(oldPin,GPIO.LOW)
	
	
	if oldPin == pin and oldPin != 200:
		#Allume la led	
		GPIO.setup(pin,GPIO.OUT)
		print "startActionRoues"
		GPIO.output(pin,GPIO.HIGH)
	elif oldPin != 200:
		#Eteind la led
		GPIO.setup(oldPin,GPIO.OUT)
		print "endActionRoues"
		GPIO.output(oldPin,GPIO.LOW)
	
	global oldPin 
	oldPin= pin
	return


def actionAttraperRelacherCanette(str):
	GPIO.setup(actionAttraperRelacher,GPIO.OUT)
	if str == "attraper":
		print "Attraper"
		GPIO.output(actionAttraperRelacher,GPIO.HIGH)
	elif str == "relacher":
		print "Relacher"
		GPIO.output(actionAttraperRelacher,GPIO.LOW)



def setup():
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pinCamGauche,GPIO.OUT)
	GPIO.setup(pinCamDroite,GPIO.OUT)

def threadMoveHead(pill2kill):
	global headMoveDirection, moveSleepDelay
	counter = moveSteps
	while True:
		# Thread is disabled
		if pill2kill.wait(moveSleepDelay):
			time.sleep(moveSleepDelay * 2)
			continue
		# Inversion de la direction
		if counter == moveSteps or counter == -moveSteps:
			headMoveDirection = not headMoveDirection
			print "Nouvelle direction:", ("Gauche" if headMoveDirection else "Droite")
			if headMoveDirection:
				print "Set pins GAUCHE = 1"
				#GPIO.output(pinCamGauche, GPIO.HIGH)
				#GPIO.output(pinCamDroite, GPIO.LOW)
			else:
				print "Set pins DROITE = 1"
				#GPIO.output(pinCamGauche, GPIO.LOW)
				#GPIO.output(pinCamDroite, GPIO.HIGH)
		# Increment
		counter += (1 if headMoveDirection else -1)
		print "Counter:", counter

def threadScanVideo(pill2kill):
	print "VIDEO"
	'''
	time.sleep(2)
	pill2kill.set() # Stop le threadMoveHead 
	time.sleep(2)
	pill2kill.clear() # Relance le threadMoveHead
	time.sleep(2)
	pill2kill.set() # Stop le threadMoveHead 
	time.sleep(2)
	pill2kill.clear() # Relance le threadMoveHead
	time.sleep(2)
	pill2kill.set() # Stop le threadMoveHead 
	time.sleep(2)
	pill2kill.clear() # Relance le threadMoveHead
	'''
	
	


	
tHead = threading.Thread(target=threadMoveHead, args=([pill2kill]))
tScan = threading.Thread(target=threadScanVideo, args=([pill2kill]))

setup()

tHead.start()
tScan.start()

tHead.join()
tScan.join()

print "Les deux threads sont termines"
