from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import multiprocessing
import signal
import RPi.GPIO as GPIO
import time
import threading
import sys

moveSleepDelay = 0.1
moveSteps = 10

pinRoueGauche = 7
pinRoueDroite = 5
pinRoueAvancer = 3
pinAttraperRelacher = 11
pinCamGauche = 15
pinCamDroite = 13
headMoveDirection = True # True = Gauche, False = Droite

mutexActionRotationHead = threading.Event()
mutexHead = threading.Event()
mutexVideo = threading.Event()

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

oldPin = 200
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



def actionRotationCamera(actionCam, temps = 0):
	print temps
	wait = int(temps)
	
	if wait != 0:
		threadFinished = False
	
	
	if actionCam == pinCamGauche:
		#GPIO.setup(actionCamGauche,GPIO.OUT)
		
		#GPIO.output(actionCamGauche,GPIO.HIGH)
		
		time.sleep(wait)
		print "Cam Gauche"
		#GPIO.output(actionCamGauche,GPIO.LOW)
		
	elif actionCam == pinCamDroite:
		#GPIO.setup(actionCamDroite,GPIO.OUT)
		
		#GPIO.output(actionCamDroite,GPIO.HIGH)
		
		time.sleep(wait)
		print "Cam Droite"
		#GPIO.output(actionCamDroite,GPIO.LOW)
	
	


	

def pinAttraperRelacherCanette(str):
	GPIO.setup(pinAttraperRelacher,GPIO.OUT)
	if str == "attraper":
		print "Attraper"
		GPIO.output(pinAttraperRelacher,GPIO.HIGH)
	elif str == "relacher":
		print "Relacher"
		GPIO.output(pinAttraperRelacher,GPIO.LOW)



def setup():
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pinCamGauche,GPIO.OUT)
	GPIO.setup(pinCamDroite,GPIO.OUT)

def threadMoveHead(mutexHead):
	global headMoveDirection, moveSleepDelay
	counter = moveSteps
	while True:
		# Thread is disabled
		if mutexHead.wait(moveSleepDelay):
			global halt
			if halt:
				print "[HALT] Head thread"
				break
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

def threadScanVideo(mutexHead, mutexVideo):
	print "VIDEO"
	
	
		
		
	# capture frames from the camera
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		image = frame.array
		gauche = cv2.line(image, ((resolutionX /2)-40, resolutionY), ((resolutionX/2)-40, 0), (255,0,0), 2)
		droite = cv2.line(image, ((resolutionX /2)+40, resolutionY), ((resolutionX/2)+40, 0), (255,255,0), 2)
		hauteur = cv2.line(image, (0, (resolutionY /2)), ((resolutionX, resolutionY/2)), (0,255,0), 2)

		face=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
		faces = face_cascade.detectMultiScale(face, 1.3, 5)
		

		if not len(faces):
			mutexHead.clear() # Relance le threadMoveHead
			
		else:
			mutexHead.set() # Stop le threadMoveHead 
			print "Ok"
			
			
			# -- Dessine un rectangle autour des visages detectes
			for (x,y,w,h) in faces:
				rect = cv2.rectangle(image,(x,y),(x+w,y+h),(255,255,0),2)
				
				centreRectangle = [x +w/2, y+h/2]
				circle = cv2.circle(image, (centreRectangle[0], centreRectangle[1]), 5, (100, 50, 50),-1)

				posCenter = [x +w/2, y+h/2]
				ret, thresh = cv2.threshold(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY),127,250,0)
				im2, contours, hierarchy = cv2.findContours(thresh, 1, 2)
				cnt = contours[0]
				M = cv2.moments(cnt)
				
				#cv2.imshow("test", thresh)

				positions = str(posCenter[0]) + " - Y :" + str(posCenter[1])
				#dimension = "DimX :" + str(resolutionX) + " DimY :" + str(resolutionY)
				cv2.putText(image, positions, (20, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
				

				
				# 1 - Get la position de la canette sur l ecran
				
				#Centre de l'ecran
				centerX = resolutionX / 2
				centerY = resolutionY / 2
				
				if(centreRectangle[0] < centerX-40):
					#Canette a gauche
					cv2.putText(image, "Gauche", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
					actionRoues(pinRoueGauche)
					actionRotationCamera(pinCamGauche)
					print "Cam Gauche"

				elif(centreRectangle[0] > centerX+40):
					#Canette a droite
					cv2.putText(image, "Droite", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
					actionRoues(pinRoueDroite)			
					actionRotationCamera(pinCamDroite)
					print "Cam Droite"

				elif(centreRectangle[0] > centerX-40 and centreRectangle[0] < centerX+40):
					#Canette au centre
					cv2.putText(image, "Avancer", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
					actionRoues(pinRoueAvancer)
					print "Avancer"
				


				'''/////////////////////////
				///////////END FCT//////////
				/////////////////////////'''


		# -- Montre l'image
		cv2.imshow("face", image)
		key = cv2.waitKey(1) & 0xFF
		rawCapture.truncate(0)
	 
		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			breakcamera.resolution = (600, 400)
			cv2.destroyAllWindows()
	
	
	while True:
		if mutexVideo.wait(1):
			print "[HALT] Video thread"
			break
		print "Video"
	
# Interrupt Signal
halt = False
def stopAll(signum, frame):
	print "Interrupt!!"
	global halt
	halt = True
	mutexHead.set()
	mutexVideo.set()
signal.signal(signal.SIGINT, stopAll)



# mutexHead.set() # Pause le threadMoveHead
# mutexVideo.set() # Stop le threadScanVideo
# stopAll() # Stop all threads

tHead = threading.Thread(target=threadMoveHead, args=([mutexHead]))
tScan = threading.Thread(target=threadScanVideo, args=([mutexHead, mutexVideo]))

setup()

try:
	tHead.start()
	tScan.start()

	while not halt:
		continue
	print "[HALT] Main thread"

except Exception as ex:
		print ex
