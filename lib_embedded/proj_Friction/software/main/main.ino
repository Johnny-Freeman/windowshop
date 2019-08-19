/*
	Libraries:
	Adafruit Neopixel 1.1.8
*/

#include <Adafruit_NeoPixel.h>

#define neopixel1 Adafruit_NeoPixel;

// Config
int usr_delay = 100; //ms between loops/refresh rates/response time between states

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

// Fixed LED pins
const int ledPin1 = 12;
const int ledPin2 = 13;

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
int encodeState[9];
int encodeDecimal = 0;
int encodePosition = 0;

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
Adafruit_NeoPixel neopixel_1 = Adafruit_NeoPixel(1, neoPin1, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel neopixel_2 = Adafruit_NeoPixel(1, neoPin2, NEO_GRBW + NEO_KHZ800);

// Define FixedLED values (these are used to control fixed LED intensity)
int fixedLED_1_brightness = 0;
int fixedLED_2_brightness = 0;

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

  // Initiate FixedLED Pins
  pinMode( ledPin1, OUTPUT);
  pinMode( ledPin2, OUTPUT);

  // Initiate Neopixel data pins
  //pinMode( neoPin1, OUTPUT);
  //pinMode( neoPin2, OUTPUT);

  delay(1000);
  // Initiate Neo Pixels
  neopixel_1.begin();
  neopixel_2.begin();
  neopixel_1.show();
  neopixel_2.show();
}

// Neopixel - display funzies
void NEO_push(){
  neopixel_1.show();
  neopixel_2.show();
}

void display_push(){
  NEO_push();
  analogWrite(ledPin1,fixedLED_1_brightness);
  analogWrite(ledPin2,fixedLED_2_brightness);
}


//Canvas (display buffer)
/* Use the following commands to set Display
 * neopixel_1.setPixelColor(0,red,green,blue,white);
 * neopixel_2.setPixelColor(0,red,green,blue,white);
 * fixedLED_1_brightness = <0 to 255>;
 * fixedLED_2_brightness = <0 to 255>;
*/
void Canvas(int encodePosition){
  //https://learn.adafruit.com/adafruit-neopixel-uberguide/arduino-library-use
  neopixel_1.setPixelColor(0,encodePosition,encodePosition,0,0);
}

int encodeArray_to_Decimal(int barry[]){
  int total = 0;
  for(int i =0; i < 8; i++){
    if (barry[i]==HIGH){
      total+= 1<<i;
    }
  }
  return total;
}

const int dict_decimal_position[128] = {127, 63, 62, 58, 56, 184, 152, 24, 8, 72, 73, 77, 79, 15, 47, 175, 191, 159, 31, 29, 28, 92, 76, 12, 4, 36, 164, 166, 167, 135, 151, 215, 223, 207, 143, 142, 14, 46, 38, 6, 2, 18, 82, 83, 211, 195, 203, 235, 239, 231, 199, 71, 7, 23, 19, 3, 1, 9, 41, 169, 233, 225, 229, 245, 247, 243, 227, 163, 131, 139, 137, 129, 128, 132, 148, 212, 244, 240, 242, 250, 251, 249, 241, 209, 193, 197, 196, 192, 64, 66, 74, 106, 122, 120, 121, 125, 253, 252, 248, 232, 224, 226, 98, 96, 32, 33, 37, 53, 61, 60, 188, 190, 254, 126, 124, 116, 112, 113, 49, 48, 16, 144, 146, 154, 158, 30, 94, 95};
int returnPosition(int encodeDecimal){
  int idx =0;
  //int indexOf
  while(!(dict_decimal_position[idx]=='\0')){
    if (dict_decimal_position[idx]== encodeDecimal){
       break;
    }
    idx++;
  }
  Serial.println(idx);
  return idx;
}

void read_encoder_state(){
  //  Reading Pin Values - StateN is superficious > modernized code
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
}

void loop() {
  // put your main code here, to run repeatedly: 
  delay(usr_delay);

  //Read from the encoder
  read_encoder_state();
  encodeDecimal = encodeArray_to_Decimal(encodeState);
  encodePosition = returnPosition(encodeDecimal);

  //Write to Display
  Canvas(encodePosition);
  display_push();
  dosomething();
}
