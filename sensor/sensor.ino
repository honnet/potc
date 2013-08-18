bool led = 0;
//float oldValue = 0;
//const float COEF = 0.9;

int sensorValue = 70;
int delta = 10;

void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(9600);

  Serial.println("B");
}

void loop() {
//  float sensorValue = analogRead(A1);
//  sensorValue = sensorValue * COEF + oldValue * (1-COEF);
  if (sensorValue>130 || sensorValue<70) {
    delta = -delta;
    Serial.println("E");
    Serial.println("V12");
    delay(2000);
    Serial.println("B");
  }

  sensorValue += delta;
  Serial.print("H");
  Serial.println(sensorValue);

  digitalWrite(13, led = !led);
  delay(1000);
}
