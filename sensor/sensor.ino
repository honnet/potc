bool led = 0;
//float oldValue = 0;
//const float COEF = 0.9;

int sensorValue = 70;
int delta = 1;

void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(9600);
}

void loop() {
//  float sensorValue = analogRead(A1);
//  sensorValue = sensorValue * COEF + oldValue * (1-COEF);
  if (sensorValue>130 || sensorValue<70)
    delta = -delta;

  sensorValue += delta; 
  
  Serial.println(sensorValue);

  digitalWrite(13, led = !led);
  delay(1000);
}
