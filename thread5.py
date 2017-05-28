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
pinRoueDroite = 1
pinRoueGauche = 2
pinRoueAvancer = 3
pinCamGauche = 5
pinCamDroite = 6
pinRoueStop = 7

pinAttraper= 4
pinRelacher= 7


#Parametres camera
resolutionX = 320
resolutionY = 240
centerX = resolutionX / 2
centerY = resolutionY / 2
angleCamera = 0

camera = PiCamera()
camera.resolution = (resolutionX, resolutionY)
camera.framerate = 32
camera.rotation = 90
rawCapture = PiRGBArray(camera, size=camera.resolution )
time.sleep(0.1)
image = ""


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
centre_canette = []
centre_zoneDepot = []
tempsTourCompletRobot = ""



def setup():		
	global tHead, tScan
	global lowerCouleurCanette, upperCouleurCanette
	global lowerCouleurZoneDepot, upperCouleurZoneDepot
	global couleurCentreCanette, couleurCentreZoneDepot
	global tempsTourCompletRobot
	
# COULEUR DE LA CANETTE	
	tempsTourCompletRobot = 60
	
	lowerCouleurCanette = [150,150,50]
	upperCouleurCanette = [180,255,255]
	couleurCentreCanette = [0, 0, 255]
	
	# COULEUR DE LA ZONE DE DEPOT	
	lowerCouleurZoneDepot = [40,100,100]
	upperCouleurZoneDepot = [60,255,255]
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
		time.sleep(0.1)	
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



def actionRotationCamera(actionCam, temps = 0, text = "", angleImpose = ""):
	global pinCamGauche, pinCamDroite
	global address, bus, lock
	global angleCamera
	wait = int(temps)
	
	
	if angleImpose == "":
		# 1 demande de rotation = 1deg
		if actionCam == pinCamGauche:
			angleCamera += -1
		elif actionCam == pinCamDroite:
			angleCamera += 1
	elif angleImpose != "" and actionCam != angleImpose:
		#Camera trop a droite, on la remet a gauche, va tendre vers [[ angleImpose ]]
		if angleCamera >= angleImpose:
			angleCamera += -1
			actionCam = pinCamGauche
		
		#Camera trop a gauche, on la remet a droite, va tendre vers [[ angleImpose ]]
		elif angleCamera <= angleImpose:
			angleCamera += 1
			actionCam = pinCamDroite
	
	if wait != 0:
		threadFinished = False
	
	mutexMethod(actionCam, text)			
	time.sleep(wait)
	
		
'''
def pinAttraperRelacherCanette(pin, text):

	mutexMethod(pin, text)
'''	
	



def orientationRobotVersCanette(centreObject):
	global centre_canette
	global pinRoueGauche, pinCamGauche
	global pinRoueDroite, pinCamDroite
	global pinRoueAvancer,centerX, centerY
	global image
	pins = []
	
	
	if(centreObject[0] <= centerX-40 and centreObject[0] != 0):
		#Canette a gauche
		cv2.putText(image, "Gauche", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)

		print "La canette est sur la gauche"
		pins = [pinCamGauche, pinRoueGauche, "[[ Gauche ]]"]
		
	elif(centreObject[0] >= centerX+40 and centreObject[0] != 0):
		#Canette a droite
		cv2.putText(image, "Droite", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
		
		print "La canette est sur la droite"
		pins = [pinCamDroite, pinRoueDroite, "[[ Droite ]]"]

	elif(centreObject[0] > centerX-40 and centreObject[0] < centerX+40 and centreObject[0] != 0):
		#Canette au centre
		cv2.putText(image, "Avancer", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
		
		print "La canette est au centre"
		pins = ["-", pinRoueAvancer, "[[ Avancer ]]"]
		
	return pins
	
		
	
	
	


def threadMoveHead(mutexHead):
	global canetteTrouvee
	global headMoveDirection, moveSleepDelay, halt
	global nombreDeRotationCameraPourLaRecherche
	global tempsTourCompletRobot
	
	
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
				nombreDeRotationCameraPourLaRecherche = nombreDeRotationCameraPourLaRecherche + 1
				headMoveDirection = not headMoveDirection
				
				print "Nouvelle direction de la camera pour recherche:", ("GAUCHE" if headMoveDirection else "DROITE")
				print "nombreDeRotationCameraPourLaRecherche", nombreDeRotationCameraPourLaRecherche
				
				
				#Compter le nombre de fois que le robot entre dans cette condition
				#Si le robot fait un tour complet (Compter combien il faut de fois),
				#et qu'il ne trouve toujours pas de canette, alors il faut le faire bouger de position
				#pendant x secondes.
				if nombreDeRotationCameraPourLaRecherche > 3:
					tempsQuartDeTourRebot = tempsTourCompletRobot/4
					nombreDeRotationCameraPourLaRecherche = 0
					
					
					
					while tempsQuartDeTourRebot != 0:
						print "Le robot tourne sur la droite car il n'a pas trouvee de canette pendant sa recherche"
						actionRoues(pinRoueGauche)	
						
						tempsQuartDeTourRebot -= 1
						#continue	
					
			else:
				print headMoveDirection
				if headMoveDirection:
					actionRotationCamera(pinCamGauche,0,"Tourne la camera sur la [[ GAUCHE ]]")
				else:
					actionRotationCamera(pinCamDroite,0,"Tourne la camera sur la [[ DROITE ]]")
				
					
			# Increment
			counter += (1 if headMoveDirection else -1)


	





def threadScanVideo(mutexHead, mutexVideo):
	#print "VIDEO"
	global image
	global lowerCouleurCanette, upperCouleurCanette
	global lowerCouleurZoneDepot, upperCouleurZoneDepot
	global couleurCentreCanette, couleurCentreZoneDepot
	global canetteAttrape, canetteTrouvee
	global centre_canette, centre_zoneDepot
	global pinAttraper, pinRelacher
	
	global pinRoueGauche, pinCamGauche
	global pinRoueDroite, pinCamDroite
	global pinRoueAvancer,centerX, centerY
	
	global tempsTourCompletRobot
	

	
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
		green = np.uint8([[[0,255,0]]])
		
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
		hsv_green = cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
		
		
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
			Cx,Cy,Cw,Ch = cv2.boundingRect(cnt2_canette)
			cv2.rectangle(blur,(Cx,Cy),(Cx+Cw,Cy+Ch),(couleurCentreCanette[0],couleurCentreCanette[1],couleurCentreCanette[2]),2)

		
		if areas_Depot :			
			cnt2_depot = contoursZoneDepot[np.argmax(areas_Depot)]
			ZDx,ZDy,ZDw,ZDh = cv2.boundingRect(cnt2_depot)
			cv2.rectangle(blur,(ZDx,ZDy),(ZDx+ZDw,ZDy+ZDh),(couleurCentreZoneDepot[0], couleurCentreZoneDepot[1], couleurCentreZoneDepot[2]),2)
		
		
		
		# Ajoute un point au centre des rectangle
		MC = cv2.moments(best_cnt_canette)
		cxMC,cyMC = int(MC['m10']/MC['m00']), int(MC['m01']/MC['m00'])
		cv2.circle(blur,(cxMC,cyMC),10,(couleurCentreCanette[0],couleurCentreCanette[1],couleurCentreCanette[2]),-1)	
		
		
		MD = cv2.moments(best_cnt_depot)
		cxMD,cyMD = int(MD['m10']/MD['m00']), int(MD['m01']/MD['m00'])
		cv2.circle(blur,(cxMD,cyMD),10,(couleurCentreZoneDepot[0], couleurCentreZoneDepot[1], couleurCentreZoneDepot[2]),-1)	








		
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
		#Si le robot a trouve la canette
		# 1 - Cherche a aligner le robot face a la canette
		#	-	Camera suit la canette, elle cherche a centrer la canette au centre de la camera
		#	-	Le robot s'oriente (tourne)
		#	-	Quand le robot avance la camera se remet au centre de son axe (RESTE A FAIRE)
		# 2 - Le robot avance
		
		#CONDITION 2
		#Si le robot ne trouve pas la canette
		#   - Rotation de la camera (*3 au max)
		#		# 1 - Si le robot trouve la canette alors voir #CONDITION 1
		#		# 2 - Si le robot ne trouve pas la canette 
		#			-	Le robot s'oriente (tourne pendant x secondes)
		#			-	Camera se remet au centre de son axe (RESTE A FAIRE)
		#			-	Recommence la #CONDITION 2 jusqu'a faire un tour sur lui meme
		#		# 3 - Si le robot n'a toujours pas trouve de canette apres avoir fait un tour sur lui meme
		#			-	 Le robot se deplace pendant x secondes (Arduino doit eviter les obstacles)
		#			-	 Recommence la #CONDITION 2
		
		
		
		#Si centre_canette = [0, 0] -> Aucune canette trouvee!
		centre_canette = [cxMC,cyMC]
		centre_zoneDepot = [cxMD,cyMD]
		
		
		
		###################################################################################
		######################								         ######################
		###################### 	 LE ROBOT N'A ENCORE RIEN ATTRAPE!	 ######################
		######################										 ######################
		###################################################################################
		#canetteAttrape = False => Le robot n'a pas encore attrape de canette
		if not canetteAttrape:
				
				
			##################################
			#								 #
			# 	 LE ROBOT NE TROUVE RIEN !	 ###################################################
			#								 #
			##################################	
				
			#La camera n'a rien dans le champs de vision
			if centre_canette == [0,0]:
				mutexHead.clear() # Relance le threadMoveHead
				
				print "Aucune canette trouvee"
				if canetteTrouvee:
					canetteTrouvee = False
					
				#actionRoues() => N'avance pas
				#actionRoues(args) => Tourne / Abvance
				actionRoues()
			
			
			
			##################################
			#								 #
			# LE ROBOT A TROUVE LA CANETTE ! ###################################################
			#								 #
			##################################
			#Si la camera a dans le champs de vision 
			#	-	La canette
			elif centre_canette != [0,0] and centre_zoneDepot == [0,0]:
				mutexHead.set() # Stop le threadMoveHead 
				
				if not canetteTrouvee:
					canetteTrouvee = True
					print "Canette trouvee"
					
				pinsOrientation = orientationRobotVersCanette(centre_canette)
				
				
				# pinsOrientation[0] == Pin de la cam
				# pinsOrientation[1] == Pin de la roue
				# pinsOrientation[2] == Message de l'action
				
				
				print "DEBUG" 
				print pinsOrientation
				print "DEBUG"
				
				
				if pinsOrientation[0] != "-":
					actionRoues(pinsOrientation[1])
					
					
				else:					
					#Le robot est dans l'axe de la canette, on la cam est a 0deg
					actionRotationCamera(pinsOrientation[1])
					
					#Remet la camera au centre ==> pinsOrientation[0] est egal a "-" 
					if angleCamera != 0:
							actionRotationCamera(pinsOrientation[0], 0, "La camera se recentre a 0 degre", 0)
				
				print pinsOrientation[2], "Direction Robot"
				
				print "\\\\\\\\\\\\\\\\\\\\\\\\"
				print "Angle de la camera"
				print angleCamera, "degres"
				print "\\\\\\\\\\\\\\\\\\\\\\\\"
			
			
			
			#####################################################
			#								 					#
			# LE ROBOT A TROUVE LA CANETTE ET LA ZONE DE DEPOT! ################################
			#								 					#
			#####################################################
			
			#Si la camera a dans le champs de vision
			#	-	La canette 
			#	-	La zone de depot	
			elif centre_canette != [0,0] and centre_zoneDepot != [0,0]:
				print "Canette et zone de depot trouvees"
				chevauchementX = False
				chevauchementY = False
				
				
				
				#Check si la canette et dans la zone de depot
				#Check les X
				if Cx >  ZDx and Cx < (ZDx + ZDw):
					chevauchementX = True
				elif (Cx + Cw) >  ZDx and Cx < (ZDx + ZDw):
					chevauchementX = True
				elif ZDx >  Cx and ZDx < (Cx + Cw):
					chevauchementX = True
				elif (ZDx + ZDw) >  Cx and (ZDx + ZDw) < (Cx + Cw):
					chevauchementX = True
				
				#Check les Y
				if chevauchementX:
					if Cy >  ZDy and Cy < (ZDy + ZDh):
						chevauchementY = True
					elif (Cy + Ch)  >  ZDy and Cy < (ZDy + ZDh):
						chevauchementY = True
					elif ZDy >  Cy and ZDy < (Cy + Ch):
						chevauchementY = True
					elif (ZDy + ZDh) >  Cy and (ZDy + ZDh) < (Cy + Ch):
						chevauchementY = True
				
				
				
				
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
						
					pinsOrientation = orientationRobotVersCanette(centre_canette)
					
					
							
					# pinsOrientation[0] == Pin de la cam
					# pinsOrientation[1] == Pin de la roue
					if pinsOrientation[0] != "-":
						actionRoues(pinsOrientation[1])
						
						
					else:					
						#Le robot est dans l'axe de la  [[ CENETTE ]], on met la cam est a 0deg
						actionRotationCamera(pinsOrientation[1])
			
						#Remet la camera au centre ==> pinsOrientation[0] est egal a "-" 
						
						if angleCamera != 0:
							actionRotationCamera(pinsOrientation[0], 0, "La camera se recentre a 0 degre", 0)


					print pinsOrientation[2], "Direction Robot"

					print "\\\\\\\\\\\\\\\\\\\\\\\\"
					print "Angle de la camera"
					print angleCamera, "degres"
					print "\\\\\\\\\\\\\\\\\\\\\\\\"
		
		
		###################################################################################
		######################								         ######################
		###################### 	  LE ROBOT A ATTRAPE UNE CANETTE 	 ######################
		######################										 ######################
		###################################################################################
		elif canetteAttrape:
			#La camera n'a rien dans le champs de vision
			if centre_zoneDepot == [0,0]:
				mutexHead.clear() # Relance le threadMoveHead
				
				print "Zone de depot non trouvee"
				
				#actionRoues() => N'avance pas
				#actionRoues(args) => Tourne / Abvance
				actionRoues()
				
				
				
			elif centre_zoneDepot != [0,0]:
				mutexHead.set() # Stop le threadMoveHead 
				
				if not canetteTrouvee:
					canetteTrouvee = True
					print "Depot trouvee"
					
				pinsOrientation = orientationRobotVersCanette(centre_zoneDepot)
				
				
				# pinsOrientation[0] == Pin de la cam
				# pinsOrientation[1] == Pin de la roue
				# pinsOrientation[2] == Message de l'action
				
				if pinsOrientation[0] != "-":
					actionRoues(pinsOrientation[1])
					
					
				else:					
					#Le robot est dans l'axe de la [[ ZONE DE DEPOT ]], on met la cam est a 0deg
					actionRotationCamera(pinsOrientation[1])
					
					#Remet la camera au centre ==> pinsOrientation[0] est egal a "-" 
					if angleCamera != 0:
							actionRotationCamera(pinsOrientation[0], 0, "La camera se recentre a 0 degre", 0)
				
				print pinsOrientation[2], "Direction Robot"
				
				print "\\\\\\\\\\\\\\\\\\\\\\\\"
				print "Angle de la camera"
				print angleCamera, "degres"
				print "\\\\\\\\\\\\\\\\\\\\\\\\"
		
			
		#########################################################
		#														#
		#	     ###											#
		# 	    # 	#											#
		#     	    #											#
		#		  ##											#
		#  		    #											#
		#	   #   #											#
		#	    ###												#
		#														#
		#														#
		# 	    Check si le robot peut attraper la canette		#
		#########################################################


		#########################################
		#								 		#
		#  LE ROBOT A DEJA ATTRAPE UNE CANETTE  ################################################
		#								 		#
		#########################################

		print "=================================="
		print "=================================="
		print "L ETAT DE LACTION ATTRAPER CANETTE"
		print canetteAttrape
		print "=================================="
		print "=================================="
		
		
		#Cx,Cy,Cw,Ch
		if areas_Canette and not canetteAttrape:	
			print "Cw*Ch"
			print Cw*Ch
			
			if Cw*Ch > 76000:
				actionRoues()
				mutexMethod(pinAttraper, "[[ ATTRAPER ]] - Robot action")
				canetteAttrape = True
			
		elif areas_Depot and canetteAttrape:			
			if ZDw*ZDh > 35000:
				#Stop des moteurs
				actionRoues()
				
				mutexMethod(pinRelacher, "[[ RELACHER ]] - Robot action")
				canetteAttrape = False
				
				#Rotation du robot a 180 degres (A CALCULER)
				time = 0
				print "time"
				while time < tempsTourCompletRobot:
					actionRoues(pinRoueDroite)
					time += 1
					print time
		
						
				
			



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
