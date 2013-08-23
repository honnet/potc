#include "potcpulse.h"

potcpulse::potcpulse() : contactSig( CONT_PIN , DEBOUNCE_LEN ),
                         bpmMedian(RUN_MED_LEN)
{

}

void potcpulse::setup(){
  minimum = 0;
  maximum = 0;
  riseCount = 0;
  curPoint=0;
  lastPoint=0;
  curPulseTime=0;
  lastPulseTime = 0;

  //Variables for timing stuff
  curTime = 0;
  lastTime = 0;
  lastPeakTime = 0;

  //variables for pulse mode
  sum=0;
  data=0;
  ref = 0;
  curmillis = 0;
  lastmillis = 0;
  contact = 0;
  pulseWcount = 0;
  curBeatTime = 0;
  lastBeatTime = 0;
  delta = 0;
  BPM = 0;

  contactMade = 0;
  contactStatus = 0;
  lastEdge=0;

  //variables for initial recording
  contactStartTime = 0;
  recordStatus = 0;
  playStart = 0;

  //variables for recording
  curRecordTime = 0;
}

void potcpulse::graphOut(){
  curTime = millis();
  long sum = 0;
  int avg = 0;
  Serial.println(analogRead(A0));
  lastTime=curTime;
}



int potcpulse::riseCounter(){
  curTime = millis();
  long sum = 0;
  int avg = 0;
  int BPM = 0;
  int BPMfound = 0;

  if( curTime -2 > lastTime ){
    lastTime = curTime;
    lastPoint = curPoint;
    curPoint = analogRead(SIG_PIN);

    if( (curPoint > lastPoint) ){
      riseCount = riseCount + (curPoint - lastPoint);
    }
    else{
      if( (riseCount > PULSE_THRESHOLD) && ( (millis()-100) > lastPeakTime)){
        lastPeakTime = millis();
        lastPulseTime = curPulseTime;
        curPulseTime = millis();
        BPM = 60000/(curPulseTime - lastPulseTime);
        if( 50 < BPM && BPM< 170){
          bpmMedian.add(BPM);
          BPMfound = 1;
        }
      }
      riseCount = 0;
    }
  }
  if( BPMfound == 1){
    return bpmMedian.getMedian();
  }
  else{
    return -1;
  }
}

//returns:
//0: Lost Contact
//1: Made Contact
//2: Continued Disconnect
//3: Recording
//4: Playing
int potcpulse::getBPM(){
  return BPM;
}

//returns:
//0: Lost Contact
//1: Made Contact
//2: Continued Disconnect
//3: Recording
//4: Start of Play
//5: Playing
int potcpulse::handlePulse(){
  checkContact();
  if( contactStatus == 0 ){
    Serial.println('E');
    endContact();
    return 0;
  }
  else if (contactStatus == 1){
    beginContact();
    return 1;
  }
  else{
    if( lastEdge == 0){ //continued disconnect
      return 2;
    }
    else if (lastEdge == 1){  //continued connect
      if( recordStatus == 1 ){
        handleRecord();
        return 3;
      }
      else {
        if ( playStart == 1 ){
          handlePlay();
          playStart = 0;
          return 4;
        }
        else{
          handlePlay();
          return 5;
        }
      }
    }
  }
}

void potcpulse::handleRecord(){
  curRecordTime = millis();
  if( curRecordTime  <  contactStartTime + RECORD_TIME ){
    //haven't finished initial recording yet
    riseCounter();
  }
  else{
    recordStatus = 0; //finished recording
    Serial.print('H');
    Serial.println(int(bpmMedian.getMedian()));
    BPM = bpmMedian.getMedian();
    playStart = 1;
  }
}

void potcpulse::handlePlay(){
  BPM = riseCounter();
  if( BPM > 0){
    Serial.print('H');
    Serial.println( BPM );
  }

}

void potcpulse::beginContact(){
  contactStartTime = millis();
  Serial.println('B');
  recordStatus = 1;
}

void potcpulse::endContact(){
  recordStatus = 0;
}

void potcpulse::checkContact(){
  contactSig.update();

  if(contactSig.fallingEdge()) {      // User has made contact
    contactStatus = 1;
    lastEdge = 1;
  }
  else if (contactSig.risingEdge()){  //User has lost contact
    contactStatus = 0;
    lastEdge=0;
  }
  else{                               //There has been no change in contact state
    contactStatus = 2;
  }

}
