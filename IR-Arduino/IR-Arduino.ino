//collects data from an analog sensor

int infrarougepin = 0;                 // analog pin du senseur
int valeur_infrarouge = 0;                 // variable de stockage

void setup()
{
  Serial.begin(9600);               // starts the serial monitor
}
 
void loop()
{
  valeur_infrarouge = analogRead(infrarougepin);       // reads the value of the sharp sensor
  Serial.println(valeur_infrarouge);            // prints the value of the sensor to the serial monitor
  delay(400);                    // wait for this much time before printing next value
}
