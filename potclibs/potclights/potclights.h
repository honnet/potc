#ifndef POTCLIGHTS_H
#define POTCLIGHTS_H

#include <Adafruit_NeoPixel.h>

//arduino pin for lights
#define PIN 8
//number of lights in strip
#define NUM_LIGHTS 35
#define MAX_BRIGHTNESS 100
#define ATTRACT_STEP_TIME 5 //step time of attract mode in ms

class potclights{
  public:
    potclights();//constructor
    void setup();//run in arduino setup function
    void fillColor();
    int numLights();

    void progressModeStart();
    void pulseModeStart();
    void handleLights(int, int);
    //void pulseSeqStart();
    void attractModeStart();

  private:
    Adafruit_NeoPixel strip;//(NUM_LIGHTS, PIN, NEO_GRB + NEO_KHZ800);
    void handleProgressBarMode();
    void handlePulseMode();
    void handleAttractMode();
    void dispPulse();
    void pulseSeqStart();
    void fillColor(uint32_t c, uint8_t b);

    //Variables for handling different modes
    //0: attract mode
    //1: progress bar
    //2: pulse show
    int lightMode;
    int progressStart;
    int progressCounter;
    //delay between progress steps
    int progressDelay;
    unsigned long lightCurTime;
    unsigned long lightLastTime;
    //variable for telling if new pulse has been detected
    unsigned long pulseStartTime;
    unsigned long attractCurTime;
    unsigned long attractLastTime;
    int attractCounter;
    int BPM;
    int lastPulseTime;
};

#endif // POTCLIGHTS_H
