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
moveSteps = 20

pinRoueDroite = 5			#A0
pinRoueGauche = 7 			#A1
pinRoueAvancer = 3			#A2
pinAttraperRelacher = 11	#A3
pinCamGauche = 15			#A4
pinCamDroite = 13			#A5

headMoveDirection = True # True = Gauche, False = Droite
canetteTrouvee = False
nombreDeRotationCameraPourLaRecherche = 0

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
camera.rotation = 90
rawCapture = PiRGBArray(camera, size=camera.resolution )
# allow the camera to warmup
time.sleep(0.1)

#init la position du carre a 0
cx = 0
cy = 0
positions = ''
font = cv2.FONT_HERSHEY_SIMPLEX
center = []


def setup():
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pinCamGauche,GPIO.OUT)
	GPIO.setup(pinCamDroite,GPIO.OUT)



oldPin = 200
def actionRoues(pin = ""):
	if pin == 200 and oldPin != 200:
		#Eteind la led	
		GPIO.setup(oldPin,GPIO.OUT)
		#print "LED off"
		GPIO.output(oldPin,GPIO.LOW)
	
	
	if oldPin == pin and oldPin != 200:
		GPIO.setup(pin,GPIO.OUT)
		#print "startActionRoues"
		GPIO.output(pin,GPIO.HIGH)
	elif oldPin != 200:
		#Eteind la led
		GPIO.setup(oldPin,GPIO.OUT)
		#print "endActionRoues"
		GPIO.output(oldPin,GPIO.LOW)
	
	
	# Arrete toutes les roues
	if pin == "":
		GPIO.output(pinRoueDroite,GPIO.LOW)
		GPIO.output(pinRoueGauche,GPIO.LOW)
		GPIO.output(pinRoueAvancer,GPIO.LOW)
		
	global oldPin 
	oldPin= pin
	return



def actionRotationCamera(actionCam, temps = 0.5):
	#print temps
	wait = int(temps)
	
	if wait != 0:
		threadFinished = False
	
	global pinCamGauche
	global pinCamDroite
	
	if actionCam == pinCamGauche:
		GPIO.output(pinCamGauche,GPIO.HIGH)
		print "Tourne la camera sur la [[ GAUCHE ]] afin de mettre la canette au centre"
		
	elif actionCam == pinCamDroite:
		GPIO.output(pinCamDroite,GPIO.HIGH)
		print "Tourne la camera sur la [[ DROITE ]] afin de mettre la canette au centre"

	
	time.sleep(wait)
	
	GPIO.output(pinCamDroite,GPIO.LOW)
	GPIO.output(pinCamGauche,GPIO.LOW)
		

def pinAttraperRelacherCanette(str):
	GPIO.setup(pinAttraperRelacher,GPIO.OUT)
	if str == "attraper":
		print "[[ Attraper canette ]] Action Robot"
		GPIO.output(pinAttraperRelacher,GPIO.HIGH)
	elif str == "relacher":
		print "[[ Relacher canette ]] Action Robot"
		GPIO.output(pinAttraperRelacher,GPIO.LOW)



def threadMoveHead(mutexHead):
	global canetteTrouvee
	
	if not canetteTrouvee:
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
				nombreDeRotationCameraPourLaRecherche = nombreDeRotationCameraPourLaRecherche + 1
				headMoveDirection = not headMoveDirection
				print "Nouvelle direction de la camera pour recherche:", ("GAUCHE" if headMoveDirection else "DROITE")
				
				global nombreDeRotationCameraPourLaRecherche 
				print "nombreDeRotationCameraPourLaRecherche", nombreDeRotationCameraPourLaRecherche
				
				if nombreDeRotationCameraPourLaRecherche > 3:
					print "Le robot tourne sur la droite car il n'a pas trouvee de canette pendant sa recherche"
					nombreDeRotationCameraPourLaRecherche = 0
					actionRoues(pinRoueGauche)
					
					
					time.sleep(moveSleepDelay * 20)
					continue
				
				if headMoveDirection:
					#print "Set pins GAUCHE = 1"
					GPIO.output(pinCamGauche, GPIO.HIGH)
					GPIO.output(pinCamDroite, GPIO.LOW)
				else:
					#print "Set pins DROITE = 1"
					GPIO.output(pinCamGauche, GPIO.LOW)
					GPIO.output(pinCamDroite, GPIO.HIGH)
			# Increment
			counter += (1 if headMoveDirection else -1)
			#print "Counter:", counter


def threadScanVideo(mutexHead, mutexVideo):
	#print "VIDEO"
	
	
	'''
	##########
	# 0 - Set la gamme de couleur a rechercher avec la camera
	##########
	'''
	color = "red"
	if color == "red":
		lower_color=np.array([150,150,50],dtype=np.uint8)
		upper_color=np.array([180,255,255],dtype=np.uint8)
	elif color == "yellow":
		lower_color=np.array([20,100,100],dtype=np.uint8)
		upper_color=np.array([30,255,255],dtype=np.uint8)
	
	
	
	
	
	
		
		
	# capture frames from the camera
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		image = frame.array
		#gauche = cv2.line(image, ((resolutionX /2)-40, resolutionY), ((resolutionX/2)-40, 0), (255,0,0), 2)
		#droite = cv2.line(image, ((resolutionX /2)+40, resolutionY), ((resolutionX/2)+40, 0), (255,255,0), 2)
		#hauteur = cv2.line(image, (0, (resolutionY /2)), ((resolutionX, resolutionY/2)), (0,255,0), 2)

		#face=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
		#faces = face_cascade.detectMultiScale(face, 1.3, 5)
		
		
		
		'''
		##########
		# 1 - Cherche une cannette en fonction de la couleur
		##########
		'''
		blur = cv2.blur(image, (3,3))
		hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

		threshw=cv2.inRange(hsv, lower_color, upper_color)
		#threshw=cv2.inRange(hsv, lower_yellow, upper_yellow)

		# find contours in the threshold image
		image, contours,hierarchy = cv2.findContours(threshw,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

		# finding contour with maximum area and store it as best_cnt
		max_area = 0
		best_cnt = 1
		areas = [cv2.contourArea(c) for c in contours]
		for cnt in contours:
			area = cv2.contourArea(cnt)
			if area > max_area:
					max_area = area
					best_cnt = cnt
		
				
		# finding centroids of best_cnt and draw a circle there
		M = cv2.moments(best_cnt)
		cx,cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
		cv2.circle(blur,(cx,cy),10,(0,0,255),-1)	
		
		#Si centreCercle = [0, 0] -> Aucune canette trouvee!
		centreCercle = [cx,cy]
		
		
		if centreCercle == [0,0]:
			mutexHead.clear() # Relance le threadMoveHead
			print "Aucune canette trouvee"
			global canetteTrouvee
			canetteTrouvee = False
			
		else:
			mutexHead.set() # Stop le threadMoveHead 
			print "Canette trouvee"
			global canetteTrouvee
			canetteTrouvee = True



		'''-----------------------'''
		
		'''
		##########
		# 2 - Get la position de la canette sur l ecran
		##########
		'''	
		#Centre de l'ecran
		centerX = resolutionX / 2
		centerY = resolutionY / 2
		
		#Si le robot trouve la canette
		# 1 - Cherche a aligner le robot face a la canette
		#	-	Camera suit la canette, elle cherche a centre la canette au centre de la camera
		#	-	Le robot s'oriente (tourne)
		# 2 - Le robot avance
		
		if(centreCercle[0] < centerX-40 and centreCercle[0] != 0):
			#Canette a gauche
			cv2.putText(image, "Gauche", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
			actionRoues(pinRoueGauche)
			actionRotationCamera(pinCamGauche)
			print "[[ Gauche ]] - Direction Robot"

		elif(centreCercle[0] > centerX+40 and centreCercle[0] != 0):
			#Canette a droite
			cv2.putText(image, "Droite", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
			actionRoues(pinRoueDroite)			
			actionRotationCamera(pinCamDroite)
			print "[[ Droite ]] - Direction Robot"

		elif(centreCercle[0] > centerX-40 and centreCercle[0] < centerX+40 and centreCercle[0] != 0):
			#Canette au centre
			cv2.putText(image, "Avancer", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
			actionRoues(pinRoueAvancer)
			print "[[ Avancer ]] - Direction Robot"

		'''-----------------------'''


		

		'''
		##########
		# 3 - Check si le rebot est assez proche pour attraper la canette
		##########
		'''
		if areas :
			cnt2 = contours[np.argmax(areas)]
			tx,ty,tw,th = cv2.boundingRect(cnt2)
			cv2.rectangle(blur,(tx,ty),(tx+tw,ty+th),(0,255,255),2)


			if tw*th > 26000:
				pinAttraperRelacherCanette("attraper")
			else:				
				pinAttraperRelacherCanette("relacher")




		# -- Montre l'image
		#cv2.imshow("face", image)
		#key = cv2.waitKey(1) & 0xFF
		#rawCapture.truncate(0)		
		cv2.imshow("can", image)
		cv2.imshow("frame", blur)
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
		#print "Video"
	
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
