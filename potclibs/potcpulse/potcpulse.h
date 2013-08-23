#ifndef POTCPULSE_H
#define POTCPULSE_H

#include <Adafruit_NeoPixel.h>
#include <RunningMedian.h>
#include <Bounce.h>

//number of lights in strip
#define NUM_LIGHTS 45
#define MAX_BRIGHTNESS 100

#define SIG_PIN A0
#define CONT_PIN 5
#define DEBOUNCE_LEN 200
#define RUN_MED_LEN 5
#define VEC_LEN 50
#define RECORD_TIME 6000 //Time to record pulses initially in ms

#define PULSE_THRESHOLD 75 //total height of a constally increasing signal for pulse detection

class potcpulse{
  public:
    potcpulse();//constructor
    void setup();//run in arduino setup function
    int handlePulse();
    void graphOut();//output raw data for debugging
    int getBPM();

  private:
    int riseCounter();
    void checkContact();
    void beginContact();
    void endContact();
    void handleRecord();
    void handlePlay();
    Bounce contactSig;
    RunningMedian bpmMedian;
    //Variables for rise counter
    //rise counter measures delta V for a constantly increasing signal
    int minimum;
    int maximum;
    int riseCount;
    int curPoint;
    int lastPoint;
    int curPulseTime;
    int lastPulseTime;

    //Variables for timing stuff
    unsigned long curTime;
    unsigned long lastTime;
    unsigned long lastPeakTime;

    //variables for pulse mode
    int dataVec[VEC_LEN];
    int sum;
    int data;
    int ref;
    long curmillis;
    long lastmillis;
    int contact;
    int pulseWcount;
    long curBeatTime;
    long lastBeatTime;
    long delta;
    int BPM;

    //Variables for contact detection
    int contactMade;
    int contactStatus;
    int lastEdge;

    //variables for init record
    unsigned long contactStartTime;
    int recordStatus; //1 for initial record mode
    int playStart;

    //variables for recording time
    unsigned long curRecordTime;

    //variable for reporting status
    int pulseStatus;
};

#endif // POTCPULSE_H
