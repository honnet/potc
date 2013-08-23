bool led = 0;
int sensorValue = 70;
int delta = 5;

void setup() {
  pinMode(11, OUTPUT);
  Serial.begin(9600);

  delay(2000);
  Serial.println("B");
}

void loop() {
  sensorValue += delta;
  Serial.print("H");
  Serial.println(sensorValue);

  if (sensorValue>130 || sensorValue<70) {
    delta = -delta;
    Serial.println("V12");
    Serial.println("E");
    delay(2000);
    Serial.println("B");
  }

  digitalWrite(11, led = !led);
  delay(500);
}
