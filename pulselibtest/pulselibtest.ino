#include <potcpulse.h>
#include <potclights.h>
#include <Adafruit_NeoPixel.h>
#include <RunningMedian.h>
#include <Bounce.h>

//pulls reset pin low to reset pi (also turns on pi if it is shutdown)
#define RESET_PIN 7
//Pull shutdown pin high to shutdown pi
#define SHUTDOWN_PIN 6

//Pushing reset button causes RESET_CTRL to be pulled down
#define RESET_CTRL 9
//Pushing shutdown button causes SHUTDOWN_CTRL to be pulled down
#define SHUTDOWN_CTRL 10


potcpulse pulse;
potclights lights;

void setup() {

  //Pi Power Control Begin
  pinMode(RESET_PIN, OUTPUT);
  digitalWrite(RESET_PIN, HIGH);

  pinMode(SHUTDOWN_PIN, OUTPUT);
  digitalWrite(SHUTDOWN_PIN, LOW);

  //test
  pinMode( 10, OUTPUT );
  digitalWrite( 10, HIGH);

  pinMode(RESET_CTRL, INPUT);
  digitalWrite(RESET_CTRL, HIGH); //Activate internal pullup

  pinMode(SHUTDOWN_CTRL, INPUT);
  digitalWrite(SHUTDOWN_CTRL, HIGH); //Activate internal pullup
  //Pi Power Control End

  pulse.setup();
  lights.setup();
  Serial.begin(9600);
  //Serial.println("setup end");
  lights.attractModeStart();
}

void loop() {
  int pulseStatus;
  int BPM;

  checkButtons();

  pulseStatus = pulse.handlePulse();
  BPM = pulse.getBPM();

  lights.handleLights( pulseStatus, BPM );
  //pulse.graphOut();
}

void checkButtons(){
  if( digitalRead(RESET_CTRL) == LOW ){
    piReset();
  }
  if( digitalRead(SHUTDOWN_CTRL) == LOW){
    piShutdown();
  }

}

void piShutdown(){
  digitalWrite(SHUTDOWN_PIN, HIGH);
  delay(2000);
  digitalWrite(SHUTDOWN_PIN, LOW);
}

void piReset(){
  digitalWrite(RESET_PIN, LOW);
  delay(1000);
  digitalWrite(RESET_PIN, HIGH);
}

