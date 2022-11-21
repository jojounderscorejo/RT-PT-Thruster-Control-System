#include <digitalWriteFast.h>

// Delay uncertainties: +- 1 us

// digitalWirteFast libary requires compile time constants
#define TRIGGER_PIN 2
#define CROWBAR_PIN 3
#define CAMERA_PIN 4

int numShots = 0;      // unitless
int fireInterval = 0;  // ms
int crowbarDelay = 0;  // us
int cameraDelay = 0; // us

void setup() {
  pinModeFast(TRIGGER_PIN, OUTPUT);
  pinModeFast(CROWBAR_PIN, OUTPUT);
  pinModeFast(CAMERA_PIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // Read data from serial inputs
  readSerial();
  // Excecuting firing sequence
  systemRepeatFire(numShots, fireInterval, crowbarDelay, cameraDelay);
}

void readSerial(){
  while (Serial.available() == 0){}
  String dataString = Serial.readString();
  dataString.trim();
  int buffer_len = dataString.length() + 1;
  char dataCharArr[buffer_len];
  dataString.toCharArray(dataCharArr, buffer_len);
  sscanf(dataCharArr, "%d,%d,%d,%d", &numShots, &fireInterval, &crowbarDelay, &cameraDelay);
  Serial.println("Number of shot: " + String(numShots) + "\n" //
                  "Firing Interval: " + String(fireInterval) + " ms \n" //
                  "Crowbar Delay: " + String(crowbarDelay) + " us \n" //
                  "Camera Delay: " + String(cameraDelay) + " us \n");
}

void systemFire(int crowbarDelay, int cameraDelay) {
  if (crowbarDelay < cameraDelay) {
    digitalWriteFast(TRIGGER_PIN, HIGH);
    delayMicroseconds(2);
    digitalWriteFast(TRIGGER_PIN, LOW);

    delayMicroseconds(crowbarDelay - 1);

    digitalWriteFast(CROWBAR_PIN, HIGH);
    delayMicroseconds(2);
    digitalWriteFast(CROWBAR_PIN, LOW);

    delayMicroseconds((cameraDelay - crowbarDelay)-1);

    digitalWriteFast(CAMERA_PIN, HIGH);
    delayMicroseconds(2);
    digitalWriteFast(CAMERA_PIN, LOW);
  } else if (crowbarDelay > cameraDelay) {
    digitalWriteFast(TRIGGER_PIN, HIGH);
    delayMicroseconds(2);
    digitalWriteFast(TRIGGER_PIN, LOW);

    delayMicroseconds(cameraDelay - 1);

    digitalWriteFast(CAMERA_PIN, HIGH);
    delayMicroseconds(2);
    digitalWriteFast(CAMERA_PIN, LOW);

    delayMicroseconds((crowbarDelay - cameraDelay)-1);

    digitalWriteFast(CROWBAR_PIN, HIGH);
    delayMicroseconds(2);
    digitalWriteFast(CROWBAR_PIN, LOW);
  };
}

void systemRepeatFire(int numShots, int fireInterval, int crowbarDelay, int cameraDelay) {
  int i = 0;
  while (i < numShots) {
    systemFire(crowbarDelay, cameraDelay);
    delay(fireInterval);
    i++;
  }
  // Reset all parameters
  numShots = 0;
  fireInterval = 0;
  crowbarDelay = 0;
  cameraDelay = 0;
}