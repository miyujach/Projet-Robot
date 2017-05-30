# Projet AsCyloom #

----------
![Image Sujet](https://raw.githubusercontent.com/cepes/robotSearchAndDestroy/b4e18d105783127b522bd345816336ddef0f7b48/t%C3%A9l%C3%A9chargement.png)

Après avoir remporté un appel d'offre sur la réalisation d'un robot "ramasseur de canette", l'entreprise DABOT dans laquelle nous travaillons dispose d'une dizaine de jours afin de présenter un prototypage du futur robot.


## Sommaire ##

[I.Sujet du projet](#isujet-du-projet)

[II.Projet AsCyloom](#iiprojet-ascyloom)

  [A.Analyse fonctionnelle](#aanalyse-fonctionnelle)

  [B.Analyse mécanique](#banalyse-mécanique)

[Schéma Electronique](#schéma-electronique)

[III.Pourquoi choisir notre robot?](#iiipourquoinous-)

[IV.Evolution possible](#ivevolution-possible)

[V.FAQ](#vfaq)

  [A.Liste des composants](#aliste-des-composants)

  [B.En cas de défaillance d'un composant](#ben-cas-de-défaillance-dun-composant)

[VI.Annexes](#viannexes)

  [A.Matériel fourni](#amatériel-fourni)

  [B.Composition de l'équipe](#bcomposition-de-l'équipe)
  
  [C.Mise en Marche](#cmiseenmarche)
  
  [D.Problème](#dprobleme)

## I.Sujet du projet ##

Le projet, nommé AsCyloom, impose de réaliser un robot qui aura les caractérisques listés ci-dessous:

- Les déchets à ramasser seront des cylindres métalliques.
- Le robot sera testé dans une zone de 20m² (4x5m)
- Le robot sera utilisé de jour
- Le robot ne sera pas piloté, il sera autonome
- La zone pourra comporter des obstacles qui peuvent être esquivés
- La zone de dépôt sera un carré rouge de 40cmx40cm



Schéma représentant le robot et son environnement:
![Image Sujet](https://github.com/miyujach/Projet-Robot/blob/master/Images/Sch%C3%A9maCCh.PNG)

Le résumé complet du projet est disponible au [lien suivant](https://github.com/miyujach/Projet-Robot/blob/master/Documentation%20Sujet/sujet.pdf)

## II.Projet AsCyloom ##

  ### A.Analyse fonctionnelle ###

Dans le Schéma suivant:
- FP correspond à fonction principale.
- FS correspond à fonction secondaire.
- FC correspond à fonction contrainte.
![Image_Analyse_Fonctionnelle](https://github.com/miyujach/Projet-Robot/blob/master/Images/analyse%20fonctionnelle.PNG)

Exemple de lecture: 
fonction Secondaire 2, l'opérateur peut paramétrer le robot.

| Fonction  | Rôle | Critères | Flexibilité |
| ----------- | ------------- | ------------- | ------------- |
| FP1 | Le robot doit permettre de ramasser des objets cylindriques | Nombre d'essais et erreurs par prise | Taux de reconnaissance des canettes / Accident contre un obstacle |
| FP2 | Le robot doit pouvoir se déplacer | Déplacement | Angle de Rotation |
| FP3 | Le robot doit pouvoir identifier des objets (canettes/obstacles/zone de stockage) | Taux de reconnaissance des canettes/ Pourcentage de reconnaissance de la Zone de stockage / Taux d'accident contre un obstacle | ------------- |
| ---------- | ------------- | ------------- | ------------- |
| FS1 | Le robot doit pouvoir se déplacer en faisant de la lumière ou un son | Diffusion de lumière et de son (mesuré en dB) | ------------- |
| FS2 | Le robot doit pouvoir être paramétrable par l’opérateur | Possibilité d'accès au composant | Accès aux prises démontable |
| FS3 | Le robot doit pouvoir s'orienter afin de retourner au dépôt tout en évitant les obstacles | Temps de retour | ------------- |
| FS4 | Le robot doit pouvoir s'orienter afin de rester dans la zone en évitant les obstacles | Déplacement | Reste dans la zone si il y a un mur |
| FS5 | Le niveau de batterie du robot doit être visible | Témoin de charge et de décharge | On doit pouvoir voir son état de charge |
| ---------- | ------------- | ------------- | ------------- |
| FC1 | Le robot doit évoluer dans une zone de 20cm² (4 x 5m) | Test sur la durée sur une surface supérieur | le robot doit rester dans la zone délimitée même si celle-ci n'a pas d'obstacle délimitant, tel qu'un mur |
| FC2 | Le robot doit être utilisé de jour | Taux de luminosité de la zone de test | ------------- |
| FC3 | Le robot doit être autonome | Nombre de raccordement physique en cas d'intervention | 1 à 2 |
| FC5 | Le robot doit avoir une zone de dépôt (40 x 40 cm) | Taille de la zone | ------- |
| FC6 | Le robot ne doit pas mettre en danger l’utilisateur | Une action non prévu interrompt le schéma initial | Délai de 1 seconde |
| FC7 | Le robot doit être resistance aux chocs | Crash-test/écrassement | Doit resister à un coups de pied ou un objet ou encore à un lancer d'origine humaine par exemple. |
| FC8 | Le robot doit être conforme aux normes CE | Habilitation | ------------- |
| FC9 | Le robot doit être resistance a l'eau | Test avec de l'eau | Resistance aux eclaboussures |
| FC10 | Le robot doit pouvoir continuer à fonctionner malgré une crevaison de l'un de ses pneus | Déplacement | Doit pouvoir retourner à sa base |
| FC11 | Le robot doit pouvoir être facile d'entretien | Pièce industriel standardisée / Temps de remplacement d'une pièce| 2 à 3 pièces non standards mais resistantes |
| FC12 | Le robot doit être en mesure de connaitre son niveau de batterie | Témoin de niveau de la batterie | ------------- |
| FC13 | Le robot être le plus esthétique possible | Esthétique| Avoir le meilleur design possible en relation avec l’identité visuelle du groupe |
| FC14 | Le robot doit avoir un coût de revient limité | Prix | Limiter le coût de revient du robot |
| FC15 | Le robot doit réaliser un parcours sur une piste en roulant le plus rapidement possible | Temps et Déplacement | Le robot doit réaliser son programme en un temps inférieur ou égal à 5 minutes |

  ### B.Analyse mécanique ###

Le robot dispose d'un chassis basique, produit en grande série. Plusieurs éléments complémentaires sont nécessaire afin de répondre à notre analyse fonctionnelle.

Du point de vue de la fonction principale 3 et selon la fonction principale 1 (i.e. l’identification d’un objet) nous avons choisi d'utiliser une webcam. Celle-ci doit être mobile. Plusieurs possibilités pour étendre son champ de vision sont possibles :
- La webcam est fixée sur le châssis : dans ce cas, ce sont les roues motrices qui permettent à la webcam d’avoir un champ de vision large.
- La webcam est mobile sur un bras articulé.

Pour ce proof of concept, nous avons décidé de choisir l'option du bras articulé, qui a l'avantage de permettre une plus grande rotation de la caméra. Celle-ci peut ainsi atteindre un axe de rotation d'un peu moins de 360°. Toutefois, nous resterons pour notre exemple sur une rotation sur un seul plan.

- Un système de pince. Toutefois, nous avons écarté cette option en raison de la complexité de l'algorithme au vu du temps de développement nécessaire pour positionner correctement la pince.
- Un système de râteau. Toutefois, celui-ci aurait pu bloquer le fonctionnement correct des roues.
- Un système de pelle. Toutefois, la complexité du système mécanique à mettre en place pour soulever l'objet afin de pouvoir faire levier nous a également décidés à éliminer cette solution.
- Un système magnétique. L'avantage de cette solution par rapport aux autres est la certitude de n'attraper que des objets en métal.

Le choix de l'équipe s’est donc porté sur l'utilisation d'un électro-aimant. Celui-ci a pour avantage de ne pas fonctionner en continu, et ce afin d’éviter qu’il ne se saisisse d’éléments magnétiques de façon imprévue.

Le dernier élément a été la mise en place d’un détecteur d'obstacle. Plusieurs choix se sont proposés à nous :
- un bouton poussoire enfin de signaler un objet face au robot.
- un récepteur à ultrason.
- un récepteur infrarouge.

Cette dernière solution a été préférée dans le but d'éviter tout signal parasite dans le détecteur et en raison de la faiblesse de son coût.
Après différentes études, l'équipe en est arrivé à la modélisation suivante :

Vue latérale:

![Modelisation Chassis1](https://github.com/cepes/robotSearchAndDestroy/blob/master/RobotFinal1.PNG)

Vue frontale:

![Modelisation Chassis2](https://raw.githubusercontent.com/cepes/robotSearchAndDestroy/master/robot%20final%202.PNG)

Vue de dessous:

![Modelisation Chassis3](https://raw.githubusercontent.com/cepes/robotSearchAndDestroy/master/Robot%20final%203.PNG)

Ci-joint un [modele 3D](https://github.com/cepes/robotSearchAndDestroy/blob/master/Robot%20Final.123dx)

  ### Schéma Electronique ###

Le schéma éléctrique est le suivant.
La Résistante de l'électro-aimant de 12,5 Ohm correspond à la resistance interne de l'electroaimant en fonctionnement.

![Circuit_Schéma_dévellopé](https://github.com/miyujach/Projet-Robot/blob/master/Sch%C3%A9ma%20%C3%A9lectrique/sch%C3%A9ma_electrique_L293D.PNG)

  ### C.UML ###

Au niveau de la liaison entre la partie mécanique et informatique. La logique de fonctionnement est la suivante :

UML de déploiement:

![UML de déploiement](https://github.com/miyujach/Projet-Robot/blob/master/UML/UML%20Deploiement.PNG)

UML d'Etat-transition:

![UML d'Etat-transition](https://github.com/miyujach/Projet-Robot/blob/master/UML/UML_EtatTransition.PNG)

UML d'activité:

![UML d'activité](https://github.com/miyujach/Projet-Robot/blob/master/UML/UML%20Activit%C3%A9.PNG)

[Fichier UML](https://github.com/miyujach/Projet-Robot/blob/master/UML/UML_Diagramme.mdj)

## III.Pourquoi choisir notre robot ? ##

Le robot AsCyloom représente l'innovation de l'entreprise DaBot. Notre robot est capable de répondre aux besoins exprimés dans la fiche technique. 
Outre les arguments exposés dans les pages précédentes, voici ce qui nous distingue de nos concurrents :
-	Avec une batterie de 20 000 Ampères, l’autonomie de notre robot est largement supérieure à celle de ses concurrents : 15 000 Ampères selon notre étude.
-	Le mouvement de la webcam via un bras articulé lors de la recherche d'un objet permet d'économiser de la batterie.
-	Son prix : 231 euros.
-	Sa résistance aux chocs
- Sa facilité d'entretien, en particulier avec sa séparation en deux étages : l'un électronique et l'autre contenant la batterie.
-	Le prix des pièces qui le composent, qui sont toutes produites en grande série.
-	De nombreuses évolutions possibles, cf. infra.


## IV.Evolutions possibles ##

| Fonction | Rôle | Critères | Flexibilité | Evolution | Faisabilité |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| FP2 | le robot doit pouvoir se déplacer | Vitesse et adhérence | ------ | Remplacement des roues par des chenilles ou/et augmentation du couple moteur| 100% |
| FP3 | le robot doit pouvoir identifier les objets cannettes/Zone de dépôt/Obstacles | Pourcentage de reconnaissance de la Zone de stockage / Taux d'accident contre un obstacle | ------------- | Permettre une reconnaissance sur plusieurs niveaux avec l’ajout d’une webcam sur le dessus du robot, manœuvrée par deux servomoteurs (<360°) | 100% |
| FS2 | le robot doit pouvoir être paramétrable par l’opérateur | Changement de configuration | Via button ou interface web | Création d'une interface web | 100% |
| FS3 | Le robot doit pouvoir s'orienter afin de retourner au dépôt tout en évitant les obstacles | Optimisation du trajet du robot | ----- | Ajout d'un système de compteur de tour du moteur et/ou cartographie | 80% |
| FS4 | Le robot doit pouvoir s'orienter afin de rester dans la zone en évitant les obstacles | Optimisation du trajet du robot | ----- | Ajout d'un système de compteur de tour du moteur et/ou cartographie | 80% |
| FS5 | le robot doit savoir quand il est chargé | Autonome | ----- | Capable de retourner à la base avant d'être à plat | 100% |
| FC3 | le robot doit être autonome | nombre de raccordement physique en cas d'intervention | ------------- | Ajout d'une bobine à induction sous le robot pour recharger la batterie | 100% |
| FC4 | le robot doit être utilisé de jour | Fonctionne avec une luminosité restreinte | ------------- | Ajout d'un projecteur avec détecteur de luminosité | 70% |
| Autre | Gestion d'une flotte de robot | Communique entre eux | ------------- | --------- | 80% |
| Autre | BigData | Analyse du lieu de ramassage récurent et optimisation du temps de ramassage | ------------- | --------- | 80% |

## V.FAQ ##

   #### A.Liste des composants ####

Vous trouverez ci-dessous la liste des différents éléments composant votre robot. Certaines parties plastiques du proof of concept étant spécifiques à notre entreprise, veuillez-vous rapprocher de nous pour obtenir une pièce de remplacement.

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

En cas de défaillance d'un composant, la procédure à suivre est la suivante : identifier le composant défectueux à l'aide d'un multimètre puis opérer un remplacement de celui-ci. Une liste des composants présents dans le robot est disponible dans cette FAQ dans la partie précédente (A. Liste des composants).
Ci-dessous le schéma électrique modélisé :

![Circuit_Schéma](https://github.com/miyujach/Projet-Robot/blob/master/Sch%C3%A9ma%20%C3%A9lectrique/mod%C3%A8le_electrique_L293D.PNG)

Un schéma électrique plus développé est disponible dans le chapitre « Projet Robot » partie Schéma électronique.

  #### C.Mise en marche ####
  
Initialement, votre robot est déjà configuré. Il vous suffit de d’alimenter sa batterie. Dans le cas d'un changement de l'arduino ou de la raspberry, insérez le code correspondant que vous trouverez à l'intérieur dudit composant.

 #### D.Probleme éventuel ####

Le robot ne s'arrête pas alors qu'un obstacle se présente à moins de 10cm du capteur. Cause : le capteur a un seuil de détection compris entre 10 cm et 1 mètre.

## VI.Annexes ##

  ### A.Matériel fournit ###

Le matériel de base fournit dans le cas de ce projet est le suivant :
N.B. : l’ensemble du matériel indiqué n’est pas indispensable ; en cas de difficulté, il vous est possible de remplacer un élément par d’autres matériels que vous pourriez vous procurer autrement.


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
