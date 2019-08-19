/*
	Libraries:
	Adafruit Neopixel 1.1.8
*/

#include <Adafruit_NeoPixel.h>

#define neopixel1 Adafruit_NeoPixel;

// These pins are input pins and realte to the BOURNS Encoder Serial EAWOJ-B24-AEO128L
const int encodePin1 = 2; // Encoder Digital Inputs 1-8
const int encodePin2 = 3;   
const int encodePin3 = 4;
const int encodePin4 = 5;
const int encodePin5 = 6;
const int encodePin6 = 7;
const int encodePin7 = 8;
const int encodePin8 = 9;

// Neopixel pins
const int neoPin1 = 10;
const int neoPin2 = 11;

// Obsolete: Variables representing high or low pin states
int State1 = 0;
int State2 = 0;
int State3 = 0;
int State4 = 0;
int State5 = 0;
int State6 = 0;
int State7 = 0;
int State8 = 0;

// Array holding encode pin states
int encodeState[8];

// Define Neopixel setup
/* Adafruit_NeoPixel strip = Adafruit_NeoPixel(1, neoPin1, NEO_GRB + NEO_KHZ800);
 *  https://learn.adafruit.com/adafruit-neopixel-uberguide/arduino-library-use
// Parameter 1 = number of pixels in strip
// Parameter 2 = pin number (most are valid)
// Parameter 3 = pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
*/
Adafruit_NeoPixel neopixel_1 = Adafruit_NeoPixel(1, neoPin1, NEO_GRB + NEO_KHZ800);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  // Defining previously declared pins on the arduino mega to be read as input and outputs.
  pinMode( encodePin1, INPUT);
  pinMode( encodePin2, INPUT);
  pinMode( encodePin3, INPUT);
  pinMode( encodePin4, INPUT);
  pinMode( encodePin5, INPUT);
  pinMode( encodePin6, INPUT);
  pinMode( encodePin7, INPUT);
  pinMode( encodePin8, INPUT);

  // Initiate Neopixel data pins
  //pinMode( neoPin1, OUTPUT);
  //pinMode( neoPin2, OUTPUT);

  delay(1000);
  // Initiate Neo Pixels
  neopixel_1.begin();
  neopixel_1.show();
}

/*
String intArraytoString(int arry[]){
  int length = sizeof(arry);
  String str[8];
  
  for (int i=0; i<=length; i++){
    str[i]=(char*)arry[i];
  }
  return String(str);
}
*/

// Neopixel funzies
int red = 240;
int blue = 120;
int green = 0;
int n=0;
void debug_neopixels(){
  neopixel_1.setPixelColor(0,red,green,blue);
  neopixel_1.show();
  
  n+=1;
  red = green / 3 + blue;
  green = green + n;
  blue = n;

  if (red>=255){
    red=0;
  }
  if (green>=255){
    green=0;
  }
  if (blue>=255){
    blue=0;
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  
  //  Reading Pin Values
  encodeState[0] = State1 = digitalRead(encodePin1);
  encodeState[1] = State2 = digitalRead(encodePin2);
  encodeState[2] = State3 = digitalRead(encodePin3);
  encodeState[3] = State4 = digitalRead(encodePin4);
  encodeState[4] = State5 = digitalRead(encodePin5);
  encodeState[5] = State6 = digitalRead(encodePin6);
  encodeState[6] = State7 = digitalRead(encodePin7);
  encodeState[7] = State8 = digitalRead(encodePin8);

  Serial.print(encodeState[0]);
  Serial.print(encodeState[1]);
  Serial.print(encodeState[2]);
  Serial.print(encodeState[3]);
  Serial.print(encodeState[4]);
  Serial.print(encodeState[5]);
  Serial.print(encodeState[6]);
  Serial.println(encodeState[7]);
  delay(100);
  
  //https://learn.adafruit.com/adafruit-neopixel-uberguide/arduino-library-use
  debug_neopixels();
}
