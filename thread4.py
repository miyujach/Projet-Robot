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
centerX = resolutionX / 2
centerY = resolutionY / 2

camera = PiCamera()
camera.resolution = (resolutionX, resolutionY)
camera.framerate = 32
camera.rotation = 90
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
tHead =""
tScan =""


#Initialisation de la position du carre
cx = 0
cy = 0
positions = ''
font = cv2.FONT_HERSHEY_SIMPLEX
center = []


#Recherches de couleurs suivantes
lowerCouleurCanette = []
upperCouleurCanette = []
lowerCouleurZoneDepot = []
upperCouleurZoneDepot = []
couleurCentreCanette = []
couleurCentreZoneDepot = []


#Autres
nombreDeRotationCameraPourLaRecherche = 0
headMoveDirection = True # True = Gauche, False = Droite
canetteTrouvee = False
canetteAttrape = False



def setup():		
	global tHead, tScan
	global lowerCouleurCanette, upperCouleurCanette
	global lowerCouleurZoneDepot, upperCouleurZoneDepot
	global couleurCentreCanette, couleurCentreZoneDepot
	
# COULEUR DE LA CANETTE	
	
	lowerCouleurCanette = [150,150,50]
	upperCouleurCanette = [180,255,255]
	couleurCentreCanette = [0, 0, 255]
	
	# COULEUR DE LA ZONE DE DEPOT	
	lowerCouleurZoneDepot = [20,100,100]
	upperCouleurZoneDepot = [30,255,255]
	couleurCentreZoneDepot = [0, 255, 0]
	
	
	# Lancement des threads
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
	global lowerCouleurCanette, upperCouleurCanette
	global lowerCouleurZoneDepot, upperCouleurZoneDepot
	global couleurCentreCanette, couleurCentreZoneDepot
	global canetteAttrape, canetteTrouvee
	
	global pinRoueGauche, pinCamGauche
	global pinRoueDroite, pinCamDroite
	global pinRoueAvancer,centerX, centerY
	
	'''
	##########
	# 0 - Set la gamme de couleur a rechercher avec la camera
	##########
	'''
	
	##################################
	#								 #
	# 	    COULEURS A DETECTER 	 ###################################################
	#								 #
	##################################
	lower_color_canette = np.array(lowerCouleurCanette,dtype=np.uint8)
	upper_color_canette = np.array(upperCouleurCanette,dtype=np.uint8)
		
	lower_color_zoneDeDepot = np.array(lowerCouleurZoneDepot,dtype=np.uint8)
	upper_color_zoneDeDepot = np.array(upperCouleurZoneDepot,dtype=np.uint8)
	
	
		
		
	# IMAGE DE LA CAMERA
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		image = frame.array
		'''
		# Lignes affiches a l'ecran
		gauche = cv2.line(image, ((resolutionX /2)-40, resolutionY), ((resolutionX/2)-40, 0), (255,0,0), 2)
		droite = cv2.line(image, ((resolutionX /2)+40, resolutionY), ((resolutionX/2)+40, 0), (255,255,0), 2)
		hauteur = cv2.line(image, (0, (resolutionY /2)), ((resolutionX, resolutionY/2)), (0,255,0), 2)
		'''
		
		
		
		
		#########################################################
		#														#
		#		##												#
		# 	   # #												#
		#     #	 #												#
		#  		 #												#
		#		 #												#
		#	 	 #												#
		#														#
		#														#
		# 	 Cherche une cannette en fonction de la couleur		#
		#########################################################
		blur = cv2.blur(image, (3,3))
		hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

		
		#matchCouleurCanette = cv2.inRange(hsv, lower_color_canette, upper_color_canette)
		#matchCouleurZoneDepot = cv2.inRange(hsv, lower_color_canette, upper_color_canette)
		
		#matchCouleurCanette = cv2.inRange(hsv, lower_color_zoneDeDepot, upper_color_zoneDeDepot)
		#matchCouleurZoneDepot = cv2.inRange(hsv, lower_color_zoneDeDepot, upper_color_zoneDeDepot)
		
		
		matchCouleurCanette = cv2.inRange(hsv, lower_color_canette, upper_color_canette)
		matchCouleurZoneDepot = cv2.inRange(hsv, lower_color_zoneDeDepot, upper_color_zoneDeDepot)
		
		
		
		
		
		
		
		
		#######################################
		#								  	  #
		# # 1 CHERCHE LES COULEURS SPECIFIEES ###################################################
		#								      #
		#######################################
		# [[ Canette ]] && [[ Zone de depot ]] contours
		image,contours,hierarchy = cv2.findContours(matchCouleurCanette,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
		imageZoneDepot,contoursZoneDepot,hierarchyZoneDepot = cv2.findContours(matchCouleurZoneDepot,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
		
		'''
		print "contours / contoursZoneDepot"
		print contours
		print contoursZoneDepot
		print "______________________________"
		'''
		
		
		#####################################################
		#								 			   	    #
		# # 2 CHERCHE LES CONTOURs AVEC LA SURFACE MAXIMALE ######################################
		#								  			   	    #
		#####################################################

		
		max_area_canette = 0
		best_cnt_canette = 1
		max_area_depot = 0
		best_cnt_depot = 1
		
		
		areas_Canette = [cv2.contourArea(c) for c in contours]
		areas_Depot = [cv2.contourArea(c) for c in contoursZoneDepot]
		
		
		# [[ Contours de la canette ]]
		for cnt_canette in contours:
			area_canette = cv2.contourArea(cnt_canette)
			if area_canette > max_area_canette:
					max_area_canette = area_canette
					best_cnt_canette = cnt_canette
		
				
		# [[ Contours de la Zone de depot ]]
		for cnt_depot in contoursZoneDepot:
			area_depot = cv2.contourArea(cnt_depot)
			if area_depot > max_area_depot:
					max_area_depot = area_depot
					best_cnt_depot = cnt_depot
		
		
		if areas_Canette :
			cnt2_canette = contours[np.argmax(areas_Canette)]
			tx,ty,tw,th = cv2.boundingRect(cnt2_canette)
			cv2.rectangle(blur,(tx,ty),(tx+tw,ty+th),(couleurCentreCanette[0],couleurCentreCanette[1],couleurCentreCanette[2]),2)
			
			print "---------------------------------"
			print "Cx1 : ", tx
			print "Cx2 : ", tx + tw
			print "---------------------------------"
		
		
		if areas_Depot :			
			cnt2_depot = contoursZoneDepot[np.argmax(areas_Depot)]
			Zx,Zy,Zw,Zh = cv2.boundingRect(cnt2_depot)
			cv2.rectangle(blur,(Zx,Zy),(Zx+Zw,Zy+Zh),(couleurCentreZoneDepot[0], couleurCentreZoneDepot[1], couleurCentreZoneDepot[2]),2)
		
			print "---------------------------------"
			print "Zx1 : ", Zx
			print "Zx2 : ", Zx + Zw
			print "---------------------------------"
		
		
		# finding centroids of best_cnt and draw a circle there
		M = cv2.moments(best_cnt_canette)
		cx,cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
		cv2.circle(blur,(cx,cy),10,(couleurCentreCanette[0],couleurCentreCanette[1],couleurCentreCanette[2]),-1)	
		
		
		MD = cv2.moments(best_cnt_depot)
		cxMD,cyMD = int(MD['m10']/MD['m00']), int(MD['m01']/MD['m00'])
		cv2.circle(blur,(cxMD,cyMD),10,(couleurCentreZoneDepot[0], couleurCentreZoneDepot[1], couleurCentreZoneDepot[2]),-1)	

		
		#####################################################
		#								 			   	    #
		# # 3 CHERCHE LES CONTOURs AVEC LA SURFACE MAXIMALE ######################################
		#								  			   	    #
		#####################################################
		
		
		#Si centre_canette = [0, 0] -> Aucune canette trouvee!
		centre_canette = [cx,cy]
		centre_zoneDepot = [cxMD,cyMD]
		
		
		if centre_canette == [0,0]:
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
		
		
		
		#canetteAttrape = False => Le robot n'a pas encore attrape de canette
		if not canetteAttrape:
			
			#La camera n'a rien dans le champs de vision
			if centre_canette == [0,0]:
				mutexHead.clear() # Relance le threadMoveHead
				
				print "Aucune canette trouvee"
				if canetteTrouvee:
					canetteTrouvee = False
				actionRoues()
			
			
			#Si la camera a dans le champs de vision 
			#	-	La canette
			elif centre_canette != [0,0] and centre_zoneDepot == [0,0]:
				mutexHead.set() # Stop le threadMoveHead 
				if not canetteTrouvee:
					canetteTrouvee = True
					print "Canette trouvee"
			
			
			
			
			'''
			ATTENTION MODIFIER LES VARIABLES CI DESSOUS SUIVANT LE CODE
			'''
			#Si la camera a dans le champs de vision
			#	-	La canette 
			#	-	La zone de depot
			elif centre_canette != [0,0] and centre_zoneDepot != [0,0]:
				
				
				chevauchementX = False
				chevauchementY = False
				
				#Check si la canette et dans la zone de depot
				#Check les X
				if Cx1 >  Zx1 and Cx1 < (Zx1 + ZL):
					chevauchementX = True
					print "Cx1 est compris entre Zx1 et (Zx1 + ZL)"
				elif Cx2 >  Zx1 and Cx1 < (Zx1 + ZL):
					chevauchementX = True
					print "Cx2 est compris entre Zx1 et (Zx1 + ZL)"
				elif Zx1 >  Cx1 and Zx1 < (Cx1 + CL):
					chevauchementX = True
					print "Zx1 est compris entre Cx1 et (Cx1 + CL)"
				elif Zx2 >  Cx1 and Zx2 < (Cx1 + CL):
					chevauchementX = True
					print "Zx2 est compris entre Cx1 et (Cx1 + CL)"
				
				#Check les Y
				if chevauchementX:
					if Cy1 >  Zy1 and Cy1 < (Zy1 + ZL):
						chevauchementY = True
						print "Cy1 est compris entre Zy1 et (Zy1 + ZL)"
					elif Cy2 >  Zy1 and Cy1 < (Zy1 + ZL):
						chevauchementY = True
						print "Cy2 est compris entre Zy1 et (Zy1 + ZL)"
					elif Zy1 >  Cy1 and Zy1 < (Cy1 + CL):
						chevauchementY = True
						print "Zy1 est compris entre Cy1 et (Cy1 + CL)"
					elif Zy2 >  Cy1 and Zy2 < (Cy1 + CL):
						chevauchementY = True
						print "Zy2 est compris entre Cy1 et (Cy1 + CL)"
				
				
				
				if chevauchementX and chevauchementY:
					print "La canette est deja dans la zone de depot"
				
					mutexHead.clear() # Relance le threadMoveHead
					if canetteTrouvee:
						canetteTrouvee = False
					actionRoues()
					
				else:
					print "La canette n'est pas dans la zone de stockage"
					
					mutexHead.set() # Stop le threadMoveHead 
					if not canetteTrouvee:
						canetteTrouvee = True
						print "Canette et zone de depot trouvees"

		


		#########################################################
		#														#
		#		 ###											#
		# 	   # 	#											#
		#     	   #											#
		#  		 #												#
		#		#												#
		#	   ######											#
		#														#
		#														#
		# 		 Get la position de la canette sur l ecran		#
		#########################################################
	
		
		#CONDITION 1
		#Si le robot trouve la canette
		# 1 - Cherche a aligner le robot face a la canette
		#	-	Camera suit la canette, elle cherche a centrer la canette au centre de la camera
		#	-	Le robot s'oriente (tourne)
		#	-	Quand le robotCamera se remet au centre de son axe (RESTE A FAIRE)
		# 2 - Le robot avance
		
		#CONDITION 2
		#Si le robot ne trouve pas la canette
		#   - Rotation de la camera (*3 au max)
		#		# 1 - Si le robot trouve la canette alors voir #CONDITION 1
		#		# 2 - Si le robot ne trouve pas la canette 
		#			-	Le robot s'oriente (tourne pendant x secondes)
		#			-	Camera se remet au centre de son axe (RESTE A FAIRE)
		#			-	Recommance la #CONDITION 2
		
		
		
		
		
		##################################
		#								 #
		# LE ROBOT A TROUVE LA CANETTE ! ###################################################
		#								 #
		##################################
		if(centre_canette[0] < centerX-40 and centre_canette[0] != 0):
			#Canette a gauche
			cv2.putText(image, "Gauche", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
			actionRoues(pinRoueGauche, "[[ Gauche ]]  - Direction Robot")
			time.sleep(0.1)
			actionRotationCamera(pinCamGauche,0,"Tourne la camera sur la [[ GAUCHE ]] afin de mettre la canette au centre")
			
			'''
			#Si la canette est sur la droite, alors la camera regarde a gauche du robot.
			#1 - Le robot tourne sur la gauche
			#2 - La camera se remet !!! PROGRESSIVEMENT !!! au centre du robot en partant sur la DROITE
			'''
		elif(centre_canette[0] > centerX+40 and centre_canette[0] != 0):
			#Canette a droite
			cv2.putText(image, "Droite", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
			actionRoues(pinRoueDroite, "[[ Droite ]]  - Direction Robot")			
			time.sleep(0.1)
			#actionRotationCamera(pinCamDroite,0,"Tourne la camera sur la [[ DROITE ]] afin de mettre la canette au centre")
			
			'''
				#Si la canette est sur la droite, alors la camera regarde a droite du robot
				#1 - Le robot tourne sur la droite
				#2 - La camera se remet  PROGRESSIVEMENT  au centre du robot en partant sur la GAUCHE
			'''

		elif(centre_canette[0] > centerX-40 and centre_canette[0] < centerX+40 and centre_canette[0] != 0):
			#Canette au centre
			cv2.putText(image, "Avancer", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
			actionRoues(pinRoueAvancer, "[[ Avancer ]]  - Direction Robot")
			
			'''
			#Si le robot est pret pour avancer c'est que potentiellement la camera est le robot sont
			#alignes par rapport a la canette
			
			#Avant de faire l'action [[ AVANCER ]] on s'assure que la camera est au centre
			#1 - Remise au centre !!! BRUTALEMENT !!! de la camera (Arduino)
			#2 - Si la canette est toujours au centre de la camera, c'est que la camera ete deja au centre
			#	 est donc que le robot est aussi aligne
			#3 - Le robot avance
			'''
			
			
		'''-----------------------'''


		

		'''
		##########
		# 3 - Check si le rebot est assez proche pour attraper la canette
		##########
		'''
		
		'''
		if areas :
			cnt2 = contours[np.argmax(areas)]
			tx,ty,tw,th = cv2.boundingRect(cnt2)
			cv2.rectangle(blur,(tx,ty),(tx+tw,ty+th),(0,255,255),2)


			if tw*th > 26000:
				pinAttraperRelacherCanette("attraper")
				canetteAttrape = False
			else:				
				pinAttraperRelacherCanette("relacher")
				canetteAttrape = True
		'''



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

setup()
