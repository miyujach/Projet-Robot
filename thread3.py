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
import smbus
import subprocess



# - Definition des ports pour la communication i2c
'''
pinRoueDroite = 5			#A0 - 0
pinRoueGauche = 7 			#A1 - 1
pinRoueAvancer = 3			#A2 - 2
pinAttraperRelacher = 11	#A3 - 3
pinCamGauche = 15			#A4 - 4
pinCamDroite = 13			#A5 - 5
'''
pinRoueDroite = 1			#A0 - 1
pinRoueGauche = 2 			#A1 - 2
pinRoueAvancer = 3			#A2 - 3
pinAttraperRelacher = 4		#A3 - 4
pinCamGauche = 5			#A4 - 5
pinCamDroite = 6			#A5 - 6
pinRoueStop = 7				#A2 - 3


#Parametres camera
resolutionX = 320
resolutionY = 240
camera = PiCamera()
camera.resolution = (resolutionX, resolutionY)
camera.framerate = 32
camera.rotation = 90
#camera.brightness = 70
rawCapture = PiRGBArray(camera, size=camera.resolution )
time.sleep(0.1)


#Parametres BUS
bus = smbus.SMBus(1)
address = 0x12
lock = threading.Lock()


#Parametres des events Threads
mutexActionRotationHead = threading.Event()
mutexHead = threading.Event()
mutexVideo = threading.Event()
moveSleepDelay = 0.1
moveSteps = 5
rotationRobot = 60


#Initialisation de la position du carre
cx = 0
cy = 0
positions = ''
font = cv2.FONT_HERSHEY_SIMPLEX
center = []



#Autres
nombreDeRotationCameraPourLaRecherche = 0
headMoveDirection = True # True = Gauche, False = Droite
canetteTrouvee = False



def setup():		
	print "setup"
	#bus.write_byte(adress, valeur-a-Send)
	
	
	
	
	
def mutexMethod(pin, text=""):
	global address, bus, lock
	time.sleep(0.1)
	lock.acquire()
	try:
		bus.write_byte(address, pin)	
		print text
		
	except IOError as ioe:
		print ioe
		#subprocess.call(['i2cdetect', '-y', '1'])
	
	finally:
		lock.release()
		
		
		
				

def actionRoues(pin = pinRoueStop, text = ""):
	#   actionRoues() = Roues arretes
	#	actionRoues(args) = Roues en marche
	global address, bus, lock
	mutexMethod(pin, text)





def actionRotationCamera(actionCam, temps = 0, text = ""):
	global pinCamGauche, pinCamDroite
	global address, bus, lock
	
	wait = int(temps)
	if wait != 0:
		threadFinished = False
	
	mutexMethod(actionCam, text)			
	time.sleep(wait)
	
		

def pinAttraperRelacherCanette(str):
	#GPIO.setup(pinAttraperRelacher,GPIO.OUT)
	'''
	if str == "attraper":
		print "[[ Attraper canette ]] Action Robot"
		#GPIO.output(pinAttraperRelacher,GPIO.HIGH)
	elif str == "relacher":
		print "[[ Relacher canette ]] Action Robot"
		#GPIO.output(pinAttraperRelacher,GPIO.LOW)
	'''


def threadMoveHead(mutexHead):
	global canetteTrouvee
	global headMoveDirection, moveSleepDelay, halt
	
	
	if not canetteTrouvee:
		counter = moveSteps
		while True:
			time.sleep(0.1)
			
			# Thread is disabled
			if mutexHead.wait(moveSleepDelay):
				if halt:
					print "[HALT] Head thread"
					break
				time.sleep(moveSleepDelay * 2)
				continue
				
				
			# Inversion de la direction
			if counter == moveSteps or counter == -moveSteps:
				global nombreDeRotationCameraPourLaRecherche
				nombreDeRotationCameraPourLaRecherche = nombreDeRotationCameraPourLaRecherche + 1
				headMoveDirection = not headMoveDirection
				
				print "Nouvelle direction de la camera pour recherche:", ("GAUCHE" if headMoveDirection else "DROITE")
				print "nombreDeRotationCameraPourLaRecherche", nombreDeRotationCameraPourLaRecherche
				
				
				if nombreDeRotationCameraPourLaRecherche > 3:
					global rotationRobot
					timeRotationRobot = rotationRobot
					nombreDeRotationCameraPourLaRecherche = 0
					
					while rotationRobot != 0:
						print "Le robot tourne sur la droite car il n'a pas trouvee de canette pendant sa recherche"
						actionRoues(pinRoueGauche)	
						
						time.sleep(0.1)
						rotationRobot -= 1
						#continue	
					
					rotationRobot = timeRotationRobot
			else:
				print headMoveDirection
				if headMoveDirection:
					#print "Set pins GAUCHE = 1"
					#GPIO.output(pinCamGauche, GPIO.HIGH)
					#GPIO.output(pinCamDroite, GPIO.LOW)
					print "Gauche"
					actionRotationCamera(pinCamGauche,0,"Tourne la camera sur la [[ GAUCHE ]]")
				else:
					#print "Set pins DROITE = 1"
					#GPIO.output(pinCamGauche, GPIO.LOW)
					#GPIO.output(pinCamDroite, GPIO.HIGH)
					print "Droite"
					actionRotationCamera(pinCamDroite,0,"Tourne la camera sur la [[ DROITE ]]")
				
				
			
					
			# Increment
			counter += (1 if headMoveDirection else -1)
			print "Counter:", counter


def threadScanVideo(mutexHead, mutexVideo):
	#print "VIDEO"
	global canetteTrouvee
	
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
		
		global canetteTrouvee
		if centreCercle == [0,0]:
			mutexHead.clear() # Relance le threadMoveHead
			
			print "Aucune canette trouvee"
			if canetteTrouvee:
				canetteTrouvee = False
			actionRoues()
			
		else:
			mutexHead.set() # Stop le threadMoveHead 
			if not canetteTrouvee:
				canetteTrouvee = True
				print "Canette trouvee"
			



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
		
		global pinRoueGauche, pinCamGauche
		global pinRoueDroite, pinCamDroite
		global pinRoueAvancer
		
		if(centreCercle[0] < centerX-40 and centreCercle[0] != 0):
			#Canette a gauche
			cv2.putText(image, "Gauche", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
			actionRoues(pinRoueGauche, "[[ Gauche ]]  - Direction Robot")
			time.sleep(0.1)
			actionRotationCamera(pinCamGauche,0,"Tourne la camera sur la [[ GAUCHE ]] afin de mettre la canette au centre")

		elif(centreCercle[0] > centerX+40 and centreCercle[0] != 0):
			#Canette a droite
			cv2.putText(image, "Droite", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
			actionRoues(pinRoueDroite, "[[ Droite ]]  - Direction Robot")			
			time.sleep(0.1)
			actionRotationCamera(pinCamDroite,0,"Tourne la camera sur la [[ DROITE ]] afin de mettre la canette au centre")

		elif(centreCercle[0] > centerX-40 and centreCercle[0] < centerX+40 and centreCercle[0] != 0):
			#Canette au centre
			cv2.putText(image, "Avancer", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
			actionRoues(pinRoueAvancer, "[[ Avancer ]]  - Direction Robot")

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
			cv2.destroyAllWindows()
			break
	
	
	while True:
		if mutexVideo.wait(1):
			print "[HALT] Video thread"
			break
	
	
	
	
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



try:
	tHead.start()
	tScan.start()

	while not halt:
		continue
	print "[HALT] Main thread"

except Exception as ex:
		print ex
