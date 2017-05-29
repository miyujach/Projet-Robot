Projet AsCyloom

----------
![Image Sujet](https://raw.githubusercontent.com/cepes/robotSearchAndDestroy/b4e18d105783127b522bd345816336ddef0f7b48/t%C3%A9l%C3%A9chargement.png)

L'objectif de ce projet est de répondre à un appel d'offre fictif au sujet de robots de nettoyage urbain.
Le projet se présente sous la forme d'un proof of concept.

## Sommaire ##

[I.Sujet du projet](#isujet-du-projet)

[II.Projet SearchAndDestroy](#iiprojet-searchanddestroy)

  [A.Analyse fonctionnelle](#aanalyse-fonctionnelle)

  [B.Analyse mécanique](#banalyse-mécanique)

[Schéma Electronique](#schéma-electronique)

[III.Pourquoi nous?](#iiipourquoinous-)

[IV.Evolution](#ivevolution)

[V.FAQ](#vfaq)

  [A.Liste des composants](#aliste-des-composants)

  [B.Default d'un composant ?](#bdefault-dun-composant-)

[VI.Annexes](#viannexes)

  [A.Matériel fourni](#amatériel-fourni)

  [B.Composition de l'équipe](#bcomposition-de-l'équipe)
  
  [C.Mise en Marche](#cmiseenmarche)
  
  [D.Problème](#dprobleme)

## I.Sujet du projet ##
Il s'agit d'un robot qui sera capable de ramasser des cylindres métalliques (canettes).
Les critères initiaux du projet sont les suivants:

- Les déchets à ramasser seront des cylindres métalliques.
- Le robot sera testé dans une zone de 20m² (4x5m)
- Le robot sera utilisé de jour
- Le robot ne sera pas piloté, il sera autonome
- La zone pourra comporter des obstacles qui peuvent être esquivés
- La zone de dépôt sera un carré rouge de 40cmx40cm

Schéma représentant le robot et son envirronnement:
![Image Sujet](https://raw.githubusercontent.com/cepes/robotSearchAndDestroy/master/schema_analyse.png)

Le résumé complet du projet est disponible au [lien suivant](https://github.com/cepes/robotSearchAndDestroy/blob/master/sujet.pdf)

## II.Projet SearchAndDestroy ##

  ### A.Analyse fonctionnelle ###

Dans le Schéma suivant:
- FP correspond à fonction principale.
- FS correspond à fonction secondaire.
- FC correspond à fonction contrainte.
![Image_Analyse_Fonctionnelle](https://raw.githubusercontent.com/cepes/robotSearchAndDestroy/master/analyse%20fonctionnelle.PNG)

| Fonction  | Rôle | Critères | Flexibilité |
| ------------- | ------------- | ------------- | ------------- |
| FP1 (fonction principale 1) | Doit permettre de ramasser des objets cylindrique | Nombre d'essai et erreur par prise | Taux de reconnaissance des canettes / Accident contre un obstacle |
| FP2 (fonction principale 2) | Doit pouvoir se déplacer | Déplacement | Angle de Rotation |
| FP3 (fonction principale 3) | Doit pouvoir identifier des objets | Taux de reconnaissance des canettes / Accident contre un obstacle | ------------- |
| ------------- | ------------- | ------------- | ------------- |
| FS1 (fonction secondaire 1) | Doit pouvoir se déplacer en faisant de la lumière ou un son | lumière dégagé et son entendu en db | ------------- |
| FS2 (fonction secondaire 2) | Doit pouvoir être paramétrable par l’opérateur | Possibilité d'accès au composant | Accès aux prises démontable |
| FS3 (fonction secondaire 3) | Doit pouvoir se situer pour retourner au dépôt en évitant les obstacles | Temps de retour | ------------- |
| FS4 (fonction secondaire 4) | Doit pouvoir se situer pour rester dans la zone en évitant les obstacles | Déplacement | Reste dans la zone si mur |
| FS5 (fonction secondaire 5) | Doit savoir quand il est chargé | témoin de charge / Décharge | Doit pouvoir voir son état de charge |
| ------------- | ------------- | ------------- | ------------- |
| FC1 (contrainte 1) | Doit évoluer dans une zone de 20cm² (4 x 5m) | test sur la durée dans une surface supérieur | Reste dans la zone meme si pas de mur |
| FC2 (contrainte 2) | Doit être utilisé de jour | Taux de luminosité de la zone de test | ------------- |
| FC3 (contrainte 3) | Doit être autonome | nombre de raccordement physique en cas d'intervention | 1 à 2 |
| FC4 (contrainte 4) | Doit esquiver des obstacles | parcour de test | ------- |
| FC5 (contrainte 5) | Doit avoir une zone de dépôt (40 x 40 cm) | taille de la zone | ------- |
| FC6 (contrainte 6) | Ne doit pas mettre en danger l’utilisateur | action non prévu interrompt le schéma initial | Délai de 1 seconde |
| FC7 (contrainte 7) | Resistance aux chocs | crashtest/écrassement | Doit resister à un coups de pied / main |
| FC8 (contrainte 8) | Conforme aux normes CE | habilitation | ------------- |
| FC9 (contrainte 9) | Resistance a l'eau | test avec de l'eau | Resistance aux eclaboussure |
| FC10 (contrainte 10) | Resistance à une crevaison | Déplacement | Doit pouvoir retourner à sa base |
| FC11 (contrainte 11) | Doit pouvoir être facile d'entretien | Pièce industriel standardisé/ Temps de remplacement d'une pièce| 2 à 3 pièces non standart mais resistante |
| FC12 (contrainte 12) | Doit pouvoir connaitre sa batteire | niveau de la batterie | ------------- |

  ### B.Analyse mécanique ###

Le robot disposant d'un chassis basique déjà produit en grande série. Plusieurs éléments sont cependant nécessaire en ajout de ce chassis afin de répondre à notre analyse fonctionnelle.

Du point de vue de la fonction principale 3 et selon les cas 1. Pour identifier un objet nous avons choisi d'utiliser une webcam.
La webcam nécessite cependant afin de pouvoir répondre à la question d'être mobile plusieurs possiblités pour étendre son champ de visionson possible:
- Fixé sur le chassis, pour augmenter le champ de vision cette tâche revient aux roues
- Mobile sur un bras articulé.

Pour ce proof of concept, nous avons décidé de prendre l'option du bras articulé en effet cette option à l'avantage de permettre une plus grande rotation de la caméra. Celle-ci peut ainsi atteindre un axe de rotation d'un peu moins de 360°. Notre exemple cependant restera sur une rotation sur un seul plan.

Du point de vue de la fonction principale 1. Il fallait un élément permettant la préhension. Plusieurs possiblités furent étudiés:
- Système de pince. Le problème pouvant être la complexité de l'algorythme au vu du temps de dévellopement pour positioner correctement la pince.
- Système de rateau. Le problème pouvant être de bloquer le fonctionnement correct des roues.
- Système de pelle. Le problème étant la complexité du système mécanique à mettre en place pour soulever l'objet afin de pouvoir faire levier.
- Système magnétique. L'avantage de cette solution par rapport aux autres et de pouvoir être sur de n'attraper que des cylindres en métal.

La solution de l'équipe fut l'utilisation d'un électro-aimant afin de ne pas avoir un aimant fonctionnant en continu et pouvant ainsi récuperé des éléments mécaniques de façon imprévu.

Après différentes études l'équipe en est arrivé à la modélisation suivante:

Vue latéral:

![Modelisation Chassis1](https://github.com/cepes/robotSearchAndDestroy/blob/master/RobotFinal1.PNG)

Vue Frontal:

![Modelisation Chassis2](https://raw.githubusercontent.com/cepes/robotSearchAndDestroy/master/robot%20final%202.PNG)

Vue de Dessous:

![Modelisation Chassis3](https://raw.githubusercontent.com/cepes/robotSearchAndDestroy/master/Robot%20final%203.PNG)

Ci-joint un [modele 3D](https://github.com/cepes/robotSearchAndDestroy/blob/master/Robot%20Final.123dx)

  ### Schéma Electronique ###

Le schéma éléctrique est le suivant. La R3 électro-aimant de 12,5 Ohm correspond à la resistance interne de l'electroaimant en fonctionnement. L'Infrarouge n'est pas représenté sur ce schéma car directement alimenté par la raspberry et connecté à celle-ci.
![Circuit_Schéma_dévellopé](https://github.com/miyujach/Projet-Robot/blob/master/Sch%C3%A9ma%20%C3%A9lectrique/sch%C3%A9ma_electrique_L293D.PNG)

  ### C.UML ###

Au niveau de la liaison entre la partie mécanique et informatique l'UML est le suivant:

UML de déploiement:

![UML de déploiement](https://github.com/miyujach/Projet-Robot/blob/master/UML/UML%20Deploiement.PNG)

UML d'activité:

![UML d'activité](https://github.com/miyujach/Projet-Robot/blob/master/UML/UML%20Activit%C3%A9.PNG)

[Fichier UML](https://github.com/miyujach/Projet-Robot/blob/master/UML/UML_Diagramme.mdj)

## III.Pourquoi nous? ##

Le robot AsCyloom représente l'innovation de l'entreprise DaBot, celui-ci est en effet capable de répondre à vos besoins exprimé ci-avant si vous n'êtes toujours pas convaincu voici quelques arguments permettant de faire la distinction avec nos concurrents.
Avec une batterie de 20 000 Ampères sont autonomie est largement supérieur à celle de ses concurrents.

De plus son coût de production tout à faire modique de 231 euros (210 euros à produire), celui-ci vous permettra de répondre à vos attentes sans vous ruiner.

Sa résistance au choc de même que sa facilité d'entretien sera aussi pour vous un critère de qualité.

## IV.Evolution ##

| Fonction  | Rôle | Critères | Flexibilité | Evolution | Faisabilité |
| FP3 | Rôle | Critères | Flexibilité | Evolution | Faisabilité |

| Fonction | Rôle | Critères | Flexibilité | Evolution | Faisabilité |
| FP3 | Doit pouvoir identifier des objets | Taux de reconnaissance des canettes/Accident contre un obstacle | ------------- | Permettre une reconnaissance sur plusieurs niveaux avec une autre webcam sur le dessus manoeuvré par deux servo-moteurs (<360°) | 100% |
| FC3 | Doit être autonome | nombre de raccordement physique en cas d'intervention | ------------- | Ajout d'une bobine à induction sous le robot pour recharger la baterrie | 100% |

## V.FAQ ##

   #### A.Liste des composants ####

Ci-dessous voici les différents éléments composants votre robot.
Certaines partie plastique du proof of concept étant spécifique à notre entreprise veuillez vous rapprochez de nous pour obtenir une pièce de remplacement.

| Matériel  | Nombre | Prix en Euros à l'unité |
| ------------- | ------------- | ------------- |
| [Raspberry pi 3](http://fr.farnell.com/raspberry-pi/rpi3-modb-16gb-noobs/sbc-raspberry-pi3-mod-b-carte/dp/2525227) | 1 | 43,59 |
| [Pi camera board](http://fr.farnell.com/raspberry-pi/rpi-noir-camera-board/raspberry-pi-noir-camera-board/dp/2510729) | 1 | 22,04 |
| [Carte micro SD](http://fr.farnell.com/transcend/tsraspi10-16g/16gb-microsd-card-preloaded-with/dp/2521753) | 1 | 11,70 |
| [Chassis](http://www.gotronic.fr/art-chassis-eco-dg008-17741.htm)  | 1 | 24,50 |
| [Electro aimant](https://www.gotronic.fr/art-electroaimant-grove-101020073-21548.htm) | 1 | 10,20 |
| [Servo moteur](http://www.gotronic.fr/art-servomoteur-sg90-19377.htm )  | 2 | 4,95 |
| [Batterie](https://www.amazon.fr/gp/product/B01422TC14/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1)  | 1 | 32,99 |
| [Interrupteur TI3](http://www.gotronic.fr/art-interrupteur-ti3-4167.htm) | 1 | 0,60 |
| [Pochette 250 condensateur ceramique](http://www.gotronic.fr/art-pochette-de-250-condensateurs-ceramiques-19398.htm) | 1 | 4,95 |
| [Assortiment diodes Zener](http://www.gotronic.fr/art-assortiment-de-diodes-zeners-0-5-w-dz050-2044.htm) | 1 | 7.90 |
| [Assortiment resistance](http://www.gotronic.fr/art-assortiment-de-610-resistances-1-4-w-2623.htm) | 1 |  11,50 |
| [Pack de cables de connexions](http://www.gotronic.fr/art-pack-de-cables-de-connexion-12411.htm) | 1 | 9,90 |
| [Arduino Uno](https://www.amazon.fr/dp/B01N91PVIS/ref=sr_1_3?ie=UTF8&qid=1495631066&sr=8-3&keywords=arduino+uno) | 1 | 9,90 |
| [Cable Alimentation Micro USB](https://www.amazon.fr/Anker-anti-emm%C3%AAlement-connecteurs-smartphones-Android/dp/B00SUX2IPE/ref=sr_1_9?ie=UTF8&qid=1495631198&sr=8-9&keywords=cable+micro+usb) | 1 | 5,99 |
| [Cable Alimentation Circuit]() | 1 |  5,99 |
| [L293D](http://www.gotronic.fr/art-l293d-14072.htm) | 1 | 3,20 | 


   #### B.Default d'un composant ? ####

En cas de défault d'un composant, il suffit d'identifier le composant défectueux à l'aide d'un multimètre et d'opérér un remplacement de celui-ci. Une liste des composants présent dans le robot est disponible dans ce FAQ à la partie liste des composants.

Ci-joint un schéma électrique modélisé, un schéma électrique dévellopé est disponible dans le chapitre Projet SearchAndDestroy partie Schéma électronique:
![Circuit_Schéma](https://github.com/miyujach/Projet-Robot/blob/master/Sch%C3%A9ma%20%C3%A9lectrique/mod%C3%A8le_electrique_L293D.PNG)

  #### C.Mise en marche ####
  
Initialement votre robot est déjà configuré. Il vous suffit juste de recharger l'alimentation de la batterie de celui-ci.
Dans le cas d'un changement de l'arduino ou de la raspberry il vous suffit d'insérer le code correspondant à l'interieur du dit composant.

 #### D.Probleme ####

Le robot ne s'arrête pas alors qu'un obstacle viens de se présenté à moins de 10cm du capteur.
Cause: Le capteur à un seuil de détection compris entre 10 cm et 1 mètre.

## VI.Annexes ##

  ### A.Matériel fournit ###

Le matériel de base fournit dans le cas de ce projet est le suivant :
Nota: Tout le matériel n’est pas obligatoire, et en cas de difficultés vous pouvez toujours le remplacer par
d’autres matériels que vous pourriez vous procurer.


| Matériel  | Nombre |
| ------------- | ------------- |
| [Raspberry pi 3](http://fr.farnell.com/raspberry-pi/rpi3-modb-16gb-noobs/sbc-raspberry-pi3-mod-b-carte/dp/2525227) | 1 |
| [Pi camera board](http://fr.farnell.com/raspberry-pi/rpi-noir-camera-board/raspberry-pi-noir-camera-board/dp/2510729) | 1 |
| [Carte micro SD](http://fr.farnell.com/transcend/tsraspi10-16g/16gb-microsd-card-preloaded-with/dp/2521753) | 1 |
| [Chassis](http://www.gotronic.fr/art-chassis-eco-dg008-17741.htm) | 1 |
| [Electro aimant](https://www.gotronic.fr/art-electroaimant-grove-101020073-21548.htm) | 1 |
| [Circuit picaxe 28x2 AXE401K](http://www.gotronic.fr/art-circuit-d-essais-pour-picaxe-18m2-chi030-11934.htm#complte_desc) | 1 |
| [Cable Picaxe](http://www.gotronic.fr/art-cable-de-telechargement-usb-axe027-11921.htm)  | 1 |
| [Servo moteur](http://www.gotronic.fr/art-servomoteur-sg90-19377.htm )  | 2 |
| [Batterie](https://www.amazon.fr/Batterie-15600mAh-Coolreall-Chargeur-Smartphone/dp/B01KFJEEES/ref=sr_1_1?ie=UTF8&qid=1489416295&sr=8-1&keywords=coolreall+15600mah) | 1 |
| [ULN2803A](http://www.gotronic.fr/art-uln2803a-10727.htm) | 3 |
| [L7805CV](http://www.gotronic.fr/art-l7805cv-1578.htm) | 2 |
| [Interrupteur TI3](http://www.gotronic.fr/art-interrupteur-ti3-4167.htm) | 1 |
| [Accu modelisme](http://www.gotronic.fr/art-accu-modelisme-nimh-9-6v-2ah-5772.htm) | 1 |
| [Kit d'isolement pour TO220](http://www.gotronic.fr/art-kit-d-isolement-pour-to220-6029.htm) | 2 |
| [Refroidisseur ML7](http://www.gotronic.fr/art-refroidisseur-ml7-6000.htm) | 2 |
| [Pochette 250 condensateur ceramique](http://www.gotronic.fr/art-pochette-de-250-condensateurs-ceramiques-19398.htm) | 1 |
| [Assortiment diodes Zener](http://www.gotronic.fr/art-assortiment-de-diodes-zeners-0-5-w-dz050-2044.htm) | 1 |
| [Assortiment resistance](http://www.gotronic.fr/art-assortiment-de-610-resistances-1-4-w-2623.htm) | 1 |
| [Pack de cables de connexions](http://www.gotronic.fr/art-pack-de-cables-de-connexion-12411.htm) | 1 |
| [Chargeur](http://www.gotronic.fr/art-chargeur-minilader-3-vl6424-5720.htm) | 1 |
| [L293D](http://www.gotronic.fr/art-l293d-14072.htm) | 1 |

  ### B.Composition de l'équipe ###

- Adrien Meltzer @github/adrienelium
- Mich Jach @github/michaeljach
- David Van Aelst @github/cepes
