#include "potclights.h"

potclights::potclights() : strip(NUM_LIGHTS, PIN, NEO_GRB + NEO_KHZ800)
{

}

void potclights::setup(){
  strip.begin();
  strip.show();

  //Variables for handling different modes
  //0: attract mode
  //1: progress bar
  //2: pulse show
  lightMode=0;
  progressStart=0;
  progressCounter=0;
  //delay between progress steps
  progressDelay=250;
  lightCurTime=0;
  lightLastTime=0;
  //variable for telling if new pulse has been detected
  pulseStartTime = 0;

  attractCurTime = 0;
  attractLastTime = 0;
  attractCounter = 0;
  lastPulseTime = 0;
}

int potclights::numLights(){
  return strip.numPixels();
}

void potclights::fillColor(){
  for(uint16_t i=0; i<strip.numPixels(); i++) {
    strip.setPixelColor(i, strip.Color(255,0,0));
    strip.setBrightness(100);
  }
  strip.show();
}

void potclights::attractModeStart(){
  fillColor(strip.Color(0,0,0),0);
  strip.show();
  lightMode=0;
  attractLastTime = millis();
  attractCounter = 0;
}

void potclights::pulseModeStart(){
  fillColor(strip.Color(0,0,0),0);
  strip.show();
  lightMode=2;
  lastPulseTime = millis();
}

void potclights::pulseSeqStart(){
  pulseStartTime = millis();
}


void potclights::handleAttractMode(){
  attractCurTime = millis();
  long timeDelta = (attractCurTime - attractLastTime);

  if( timeDelta > ATTRACT_STEP_TIME ){
    attractLastTime = attractCurTime;
    int foo = attractCounter%510;

    if( foo < 255){
      fillColor(strip.Color(255,0,0), foo);
    }
    else if (foo >255 && foo < 510){
      fillColor( strip.Color(255,0,0), 255-( foo -255)     );
    }
    attractCounter++;
  }
}

void potclights::dispPulse(){
  long time = millis();
  long timeDelta = (time - pulseStartTime);

  if( timeDelta<255){
    fillColor(strip.Color(255,0,0), timeDelta);
  }
  else if ( timeDelta>255 && timeDelta < 510){
    fillColor(strip.Color(255,0,0), 255-( timeDelta -255));
  }
  else{
    fillColor(strip.Color(0,0,0),0);
  }
}

void potclights::handlePulseMode(){
  int curTime = millis();
  if( curTime > 60000/BPM + lastPulseTime ){
    lastPulseTime = curTime;
    pulseSeqStart();
  }
  dispPulse();
}

void potclights::progressModeStart(){
  fillColor(strip.Color(0,0,0),0);
  strip.show();
  strip.setBrightness(MAX_BRIGHTNESS);
  lightMode=1;
  progressCounter = 0;
  lightLastTime = millis();
}

void potclights::handleLights(int pulseStatus, int BPMin){

  if( BPMin > 0){
    BPM = BPMin;
  }

  if( pulseStatus == 0){
    attractModeStart();
  }
  else if ( pulseStatus == 1){
    progressModeStart();
  }
  else if ( pulseStatus == 4 ){
    pulseModeStart();
  }

  if( lightMode == 0){
    handleAttractMode();
  }
  else if( lightMode == 1){
    handleProgressBarMode();
  }
  else if (lightMode == 2){
    handlePulseMode();
  }
}

void potclights::handleProgressBarMode(){
  lightCurTime = millis();
  if( lightCurTime > lightLastTime + progressDelay){
    strip.setPixelColor(progressCounter, strip.Color(255,0,0));
    strip.setPixelColor(strip.numPixels()-1 - progressCounter,strip.Color(255,0,0));
    strip.show();
    progressCounter++;
    lightLastTime = lightCurTime;
  }
}

void potclights::fillColor(uint32_t c, uint8_t b){
  for(uint16_t i=0; i<strip.numPixels(); i++) {
    strip.setPixelColor(i, c);
    strip.setBrightness(b);
  }
  strip.show();
}
