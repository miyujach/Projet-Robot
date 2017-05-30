#!/usr/bin/python2.7

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
pinRelacher= 8
pinInfrarouge= 9
initCamera = 10
pinRoueReculer = 11


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
moveSteps = 10
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
zoneDepotTrouvee = False
centre_canette = []
centre_zoneDepot = []
tempsTourCompletRobot = 0
angleRotationSteps = 0
tempsDeplacementRobotDansPieceSiAucunObjetTrouve = ""



def setup():		
	global tHead, tScan
	global lowerCouleurCanette, upperCouleurCanette
	global lowerCouleurZoneDepot, upperCouleurZoneDepot
	global couleurCentreCanette, couleurCentreZoneDepot
	global tempsTourCompletRobot, angleRotationSteps, tempsDeplacementRobotDansPieceSiAucunObjetTrouve
	global angleCamera
	
# COULEUR DE LA CANETTE	
	tempsTourCompletRobot = 20.4
	angleRotationSteps = 16
	tempsDeplacementRobotDansPieceSiAucunObjetTrouve = 10
	
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
	
	
	#Intialise la camera a 0 degre
	response = mutexMethod(initCamera, "Initialisation de la camera [[[ ANGLE = 0 DEGRES ]]")
	angleCamera = 0
	print "Angle de la camera"
	print angleCamera
	print "------------------"

	
	try:
		tHead.start()
		tScan.start()

		while not halt:
			continue
		print "[HALT] Main thread"
 
	except Exception as ex:
			print ex
	
	
	
	
def mutexMethod(pin, text="", wantResponse = False):
	global address, bus, lock
	lock.acquire()
	myResponse = 0
	
	try:
		bus.write_byte(address, pin)
		
		time.sleep(0.1)	
		#print text
		
		if wantResponse:
			myResponse = bus.read_byte(address)
		else:
			myResponse = ""
		
	except IOError as ioe:
		print ioe
	
	finally:
		lock.release()
		
	return myResponse
		
		
		
		
def actionInfrarouge(wantResponse = False):
	pin = pinInfrarouge
	text = ""

	response = mutexMethod(pin, text, wantResponse)
	print "response :", response

	if response == 1:
		response = True
	else:
		response = False

	print "Response Arduino:", response

	return response
		
		
		
		
		
def actionRoues(pin = pinRoueStop, text = ""):
	global pinRoueAvancer, pinRoueReculer
	global tempsTourCompletRobot, angleRotationSteps
	#   actionRoues() = Roues arretes
	#	actionRoues(args) = Roues en marche
	
	
	
	
	if pin == pinRoueAvancer:
		#Test si objet en face du robot
		
		responseInfrarouge = actionInfrarouge(True)
		if responseInfrarouge != "" and responseInfrarouge == True:
			#Si responseInfrarouge = True => Mur en face
			#Si responseInfrarouge = False => Rien en face
			
			
			while responseInfrarouge:
				#Si la read_byte infrarouge renvoit True ou False => Code fonctionne
				#Sinon l'adapter
				
				
				#Rotation du robot
				temps = 0
				while temps < 5.1:
					actionRoues(pinRoueReculer, "[[ Le robot recule car il y a un OBSTACLE en face ]]")
					temps += 1
					
					
				print "responseInfrarouge dans le while :", responseInfrarouge
				responseInfrarouge = actionInfrarouge(True)
				print "responseInfrarouge dans le while apres:", responseInfrarouge
					
		else:
			response = mutexMethod(pin, text)
		
	else:
		response = mutexMethod(pin, text)









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
	
	
	
	


def orientationRobotVersCanette(centreObject):
	global centre_canette
	global pinRoueGauche, pinCamGauche
	global pinRoueDroite, pinCamDroite
	global pinRoueAvancer,centerX, centerY
	global image
	pins = []
	
	
	# Si le cercle est en haut a gauche
	# Si centreObject[0] == 0
	# Si centreObject[1] == 1
	
	#-------------------------------------------------
	#Si centreObject[0] == 0 et centreObject[1] == 20
	#Si centreObject[0] == 20 et centreObject[1] == 20
	#Si centreObject[0] == 20 et centreObject[1] == 0
	#Si centreObject[0] == 0 et centreObject[1] == 0
	
	if centreObject[0] != 0 or centreObject[1] != 0:
	
		if(centreObject[0] <= centerX-40):
			#Canette a gauche
			cv2.putText(image, "Gauche", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)

			#print "La canette est sur la gauche"
			pins = [pinCamGauche, pinRoueGauche, "[[ Gauche ]]"]
			
		elif(centreObject[0] >= centerX+40):
			#Canette a droite
			cv2.putText(image, "Droite", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
			
			#print "La canette est sur la droite"
			pins = [pinCamDroite, pinRoueDroite, "[[ Droite ]]"]

		elif(centreObject[0] >= centerX-40 and centreObject[0] <= centerX+40):
			#Canette au centre
			cv2.putText(image, "Avancer", (150, 230), font, 0.5, (255,255,255),2,cv2.LINE_AA)
			
			#print "La canette est au centre"
			pins = ["-", pinRoueAvancer, "[[ Avancer ]]"]
			
		else:
			print "!!! Je passe dans cette condition alors qu'il ne faut pas !!!"
			print "centreObject", centreObject
			print "/////////////////////////////////////////////////////////////" 
		
	return pins
	
		
		
		

def threadMoveHead(mutexHead):
	global canetteTrouvee, moveSteps
	global headMoveDirection, moveSleepDelay, halt
	global nombreDeRotationCameraPourLaRecherche
	global tempsTourCompletRobot, angleRotationSteps, tempsDeplacementRobotDansPieceSiAucunObjetTrouve
	
	nbFoisQueLeRobotATourne = 0
	
	counter = 0
	while True:
		time.sleep(0.1)
		
		
		
		# Thread is disabled
		if mutexHead.wait(moveSleepDelay):
			if halt:
				print "[HALT] Head thread"
				break
			time.sleep(moveSleepDelay * 2)
			continue
			
		
		#Si canetteTrouvee = False ou zoneDepotTrouvee = False
		if not canetteTrouvee or not zoneDepotTrouvee:	
				
			# Inversion de la direction
			if counter == moveSteps or counter == -moveSteps:
				nombreDeRotationCameraPourLaRecherche = nombreDeRotationCameraPourLaRecherche + 1
				headMoveDirection = not headMoveDirection
				
				#print "Nouvelle direction de la camera pour recherche:", ("GAUCHE" if headMoveDirection else "DROITE")
				#print "nombreDeRotationCameraPourLaRecherche", nombreDeRotationCameraPourLaRecherche
				
				
				#Compter le nombre de fois que le robot entre dans cette condition
				#Si le robot fait un tour complet (Compter combien il faut de fois),
				#et qu'il ne trouve toujours pas de canette, alors il faut le faire bouger de position
				#pendant x secondes.
				
				if nombreDeRotationCameraPourLaRecherche > 3:
					tempsQuartDeTourRebot = tempsTourCompletRobot/angleRotationSteps
					nombreDeRotationCameraPourLaRecherche = 0
					
					
					
					while tempsQuartDeTourRebot >= 0:
						print "Le robot tourne sur la gauche car il n'a pas trouvee de canette pendant sa recherche"
						actionRoues(pinRoueGauche)	
						
						tempsQuartDeTourRebot -= 1
						nbFoisQueLeRobotATourne += 1 
						
						#continue	
					
					print "je sors"
					
					#Si le robot a fait un tour sur lui meme, alors on le fait rotation  gauche + avancer
					#On rajoute une [[ rotation a gauche ]] en plus de la faire avancer afin,
					#que le robot ne reste pas bloque dans certaines circonstances
					if nbFoisQueLeRobotATourne == angleRotationSteps:
						nbFoisQueLeRobotATourne = 0
						
						rotationAGauche = tempsTourCompletRobot/angleRotationSteps
						while rotationAGauche >= 0:
							#Robot tourne a gauche
							actionRoues(pinRoueGauche, "Le robot tourne a [[ GAUCHE ]] car il ne trouve pas de canette apres avoir fait un tour sur lui meme")
							rotationAGauche -= 1
						
						deplacement_robot_piece = tempsDeplacementRobotDansPieceSiAucunObjetTrouve
						while deplacement_robot_piece >= 0:
							#Avancer
							actionRoues(pinRoueAvancer, "Le robot [[ AVANCE ]] car il ne trouve pas de canette apres avoir fait un tour sur lui meme")
									
							print "================================================="
							print "================================================="
							print "---- Le robot change de place car il n'a pas ----"
							print "trouve de canette malgre son tour sur lui meme !!"
							print "-------------------------------------------------"
							print "================================================="
							print "================================================="
							
							deplacement_robot_piece -= 1
						
					
			else:
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
	global canetteAttrape, canetteTrouvee, zoneDepotTrouvee
	global centre_canette, centre_zoneDepot
	global pinAttraper, pinRelacher
	
	global pinRoueGauche, pinCamGauche
	global pinRoueDroite, pinCamDroite
	global pinRoueAvancer,centerX, centerY
	
	global tempsTourCompletRobot, zoneDepotTrouvee
	

	
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
		
		
		# Lignes affiches a l'ecran
		#gauche = cv2.line(image, ((resolutionX /2)-40, resolutionY), ((resolutionX/2)-40, 0), (255,0,0), 2)
		#droite = cv2.line(image, ((resolutionX /2)+40, resolutionY), ((resolutionX/2)+40, 0), (255,255,0), 2)
		#hauteur = cv2.line(image, (0, (resolutionY /2)), ((resolutionX, resolutionY/2)), (0,255,0), 2)
		
		
		
		
		
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
				
				#print "Aucune canette trouvee"
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
				
				if not canetteTrouvee or not canetteTrouvee:
					canetteTrouvee = True
					print "Canette trouvee"
				
				pinsOrientation = orientationRobotVersCanette(centre_canette)
				
				
				
				# pinsOrientation[0] == Pin de la cam
				# pinsOrientation[1] == Pin de la roue
				# pinsOrientation[2] == Message de l'action				
				if pinsOrientation[0] != "-":
					actionRoues(pinsOrientation[1])
					print "pinsOrientation[1] : ", pinsOrientation[1]
					
				else:					
					#Le robot est dans l'axe de la canette, on la cam est a 0deg
					#actionRotationCamera(pinsOrientation[1])
					actionRoues(pinsOrientation[1])
					
					#Remet la camera au centre ==> pinsOrientation[0] est egal a "-" 
					if angleCamera != 0:
							actionRotationCamera(pinsOrientation[0], 0, "La camera se recentre a 0 degre", 0)
				
				
		
			
			
			
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


		
		###################################################################################
		######################								         ######################
		###################### 	  LE ROBOT A ATTRAPE UNE CANETTE 	 ######################
		######################										 ######################
		###################################################################################
		elif canetteAttrape:
			#La camera n'a rien dans le champs de vision
			if centre_zoneDepot == [0,0]:
				mutexHead.clear() # Relance le threadMoveHead
				
				print "Zone de depot non trouvee : ", zoneDepotTrouvee
				
				#actionRoues() => N'avance pas
				#actionRoues(args) => Tourne / Abvance
				actionRoues()
				
				
				
			elif centre_zoneDepot != [0,0]:
				mutexHead.set() # Stop le threadMoveHead 
				
				if not zoneDepotTrouvee:
					zoneDepotTrouvee = True
					print "Depot trouve"
					
				pinsOrientation = orientationRobotVersCanette(centre_zoneDepot)
				
				
				# pinsOrientation[0] == Pin de la cam
				# pinsOrientation[1] == Pin de la roue
				# pinsOrientation[2] == Message de l'action
				
				if pinsOrientation[0] != "-":
					actionRoues(pinsOrientation[1])
					
					
				else:					
					#Le robot est dans l'axe de la [[ ZONE DE DEPOT ]], on met la cam est a 0deg
					actionRoues(pinsOrientation[1])
					
					#Remet la camera au centre ==> pinsOrientation[0] est egal a "-" 
					if angleCamera != 0:
							actionRotationCamera(pinsOrientation[0], 0, "La camera se recentre a 0 degre", 0)
				
				
		
			
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

				
		
		#Cx,Cy,Cw,Ch
		if areas_Canette and not canetteAttrape:	
			#print "Cw*Ch"
			#print Cw*Ch
			
			if Cw*Ch > 50000:
				actionRoues()
				mutexMethod(pinAttraper, "[[ ATTRAPER ]] - Robot action")
				canetteAttrape = True
			
		elif areas_Depot and canetteAttrape:			
			if ZDw*ZDh > 35000:
				#Stop des moteurs
				actionRoues()
				
				mutexMethod(pinRelacher, "[[ RELACHER ]] - Robot action")
				canetteAttrape = False
				zoneDepotTrouvee = False
				
				
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
	actionRoues()
signal.signal(signal.SIGINT, stopAll)



# mutexHead.set() # Pause le threadMoveHead
# mutexVideo.set() # Stop le threadScanVideo
# stopAll() # Stop all threads

setup()
	
