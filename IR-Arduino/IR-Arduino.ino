//collects data from an analog sensor

int infrarougepin = 0;                 // analog pin du senseur
int valeur_infrarouge = 0;                 // variable de stockage

void setup()
{
  Serial.begin(9600);               // starts the serial monitor
}
 
void loop()
{
  valeur_infrarouge = analogRead(infrarougepin); // lecture de la valeur retour du capteur
  if(valeur_infrarouge < analogRead(infrarougepin) and analogRead(infrarougepin) >= 560)
  {
    Serial.println(1);  //un obstacle est présent
  }
  else{
    Serial.println(0);// la voie est libre
  }
}
