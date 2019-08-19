// THIS CODE IS DESIGNED TO BE USED IN CONJUCTION WITH THE TRD CUTAWAY
// 10K resistors for Encoder
// Last Revision = June 6 2016
// Any Questions Contact Nicholas Rivero riveronamech@gmail.com
#include <Adafruit_NeoPixel.h>


#define NEOPIXEL_PISTON_1 7
#define NEOPIXEL_PISTON_2 8
#define NEOPIXEL_CYL_1 9
#define NEOPIXEL_CYL_2 11
#define NEOPIXEL_CYL_3 10
#define NEOPIXEL_CYL_4 12
Adafruit_NeoPixel strip_piston_1 = Adafruit_NeoPixel(4, NEOPIXEL_PISTON_1, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip_piston_2 = Adafruit_NeoPixel(4, NEOPIXEL_PISTON_2, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip_cyl_1 = Adafruit_NeoPixel(1, NEOPIXEL_CYL_1, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip_cyl_2 = Adafruit_NeoPixel(1, NEOPIXEL_CYL_2, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip_cyl_3 = Adafruit_NeoPixel(1, NEOPIXEL_CYL_3, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip_cyl_4 = Adafruit_NeoPixel(1, NEOPIXEL_CYL_4, NEO_GRBW + NEO_KHZ800);


void setColor1(int R1, int G1, int Bl1, int W1);
void updateStringValue();


// These pins are input pins and realte to the BOURNS Encoder Serial EAWOJ-B24-AEO128L
const int Pin8 = 2; // Encoder Digital Inputs 1-8
const int Pin7 = 3;   
const int Pin6 = 4;
const int Pin5 = 5;
const int Pin4 = A2;
const int Pin3 = A1;
const int Pin2 = A0;
const int Pin1 = 6;

// These pins are output pins and control an individual LED
const int Red1 =  2;      // Red LED CYL #1
const int Green1 = 3;   // Green LED  CYL #1
const int Blue1  =  4;   // Blue LED CYL #1
const int White1 = 5;   // White LED CYL #1
const int Fuel1  = 6;   // Single BLUE LED FOR Fuel

//These are comented out due to TRD only having one Cylinder animated 
// const int Red1 = 6;      // Red LED CYL #2
//const int Green1 = 7;    // Green LED CYL #2
//const int Blue1 = 8;   // Blue LED CYL #2
//const int Spark1 = 9;  // Fuel LED CYL #2
//const int TDCLED = 10;  // LED For Timing Engine at TDC




////                      ######        LED TIMING INFORMATION HERE    #######
// These are CAM degree positions from 0-360 to devide the 128 positons of the encoder and are used in a conversion process later on. This is where you adjust the on and of times of LEDS
//                      ######        CYL #1      ###########
float IntOn1 = 13;   // Intake LED cyl #1  on ( Deg )
float IntOff1 = 113;   // Intake LED cyl #1 off ( Deg )
float ComOn1 = 113;   // Compression LED cyl #1  on ( Deg )
float ComOff1 = 197; // Compression LED cyl #1 off ( Deg )
float SparkOn1 = 197;
float SparkOff1 = 203;
float PowOn1 = 204;
float PowOff1 = 281;
float ExhOn1 = 281;    // Exhaust LED cyl #1 on ( Deg )
float ExhOff1 = 13;    // Exhaust LED cyl #1 off ( Deg )
float FuelOn1 = 177 ;   // Fuel LED cyl #1  on ( Deg )
float FuelOff1 = 102;   // Fuel LED cyl #1 off ( Deg )


float TDCon = 160;       // Indicate TDC LED on the PCB board so you can set the motor to TDC then 


// Variables
float string_value = 0;  //Variable used to store position value, between 0 and 127

int State1 = 0;   // Variables representing high or low pin states
int State2 = 0;
int State3 = 0;
int State4 = 0;
int State5 = 0;
int State6 = 0;
int State7 = 0;
int State8 = 0; 
void setup()
{  

  strip_piston_1.begin();
  strip_piston_2.begin();
  strip_cyl_1.begin();
  strip_cyl_2.begin();
  strip_cyl_3.begin();
  strip_cyl_4.begin();
  for(int i=0; i<4; i++)
  {
    strip_piston_1.setPixelColor(i, 0x00, 0x00, 0x00);
    strip_piston_2.setPixelColor(i, 0x00, 0x00, 0x00);
  }
  strip_cyl_1.setPixelColor(0, 0x00, 0x00, 0x00, 0x00);
  strip_cyl_2.setPixelColor(0, 0x00, 0x00, 0x00, 0x00);
  strip_cyl_3.setPixelColor(0, 0x00, 0x00, 0x00, 0x00);
  strip_cyl_4.setPixelColor(0, 0x00, 0x00, 0x00, 0x00);
  strip_piston_1.show();
  strip_piston_2.show();
  strip_cyl_1.show();
  strip_cyl_2.show();
  strip_cyl_3.show();
  strip_cyl_4.show();
  
  // Defining previously declared pins on the arduino mega to be read as input and outputs.
  pinMode( Pin1, INPUT);
  pinMode( Pin2, INPUT);
  pinMode( Pin3, INPUT);
  pinMode( Pin4, INPUT);
  pinMode( Pin5, INPUT);
  pinMode( Pin6, INPUT);
  pinMode( Pin7, INPUT);
  pinMode( Pin8, INPUT);

  /*pinMode ( Red1, OUTPUT );
  pinMode ( Green1, OUTPUT );
  pinMode ( Blue1, OUTPUT );
  pinMode ( White1, OUTPUT );
  pinMode ( Fuel1, OUTPUT );*/


  Serial.begin(9600);
  delay(1000);
}

void loop()
{  
  updateStringValue();

  char strip_cyl4_red = 0x00;
  char strip_cyl4_green = 0x00;
  char strip_cyl4_blue = 0x00;
  char strip_cyl4_white = 0x00;
  if(string_value >= 14 && string_value < 52)
  {
    // Blue
    strip_cyl4_red = 0x00;
    strip_cyl4_green = 0x00;
    strip_cyl4_blue = 0xFF;
    strip_cyl4_white = 0x00;
  }
  else if(string_value >= 52 && string_value < 77)
  {
    // Turqoise
    strip_cyl4_red = 0x40;
    strip_cyl4_green = 0xD0;
    strip_cyl4_blue = 0xE0;
    strip_cyl4_white = 0x00;
  }
  else if(string_value >= 77 && string_value < 80)
  {
    // White
    strip_cyl4_red = 0x00;
    strip_cyl4_green = 0x00;
    strip_cyl4_blue = 0x00;
    strip_cyl4_white = 0xFF;
  }
  else if(string_value >= 80 && string_value < 117)
  {
    // Red
    strip_cyl4_red = 0xFF;
    strip_cyl4_green = 0x00;
    strip_cyl4_blue = 0x00;
    strip_cyl4_white = 0x00;
  }
  else if(string_value >= 117 && string_value <= 127)
  {
    // Orange
    strip_cyl4_red = 0xFF;
    strip_cyl4_green = 0x45;
    strip_cyl4_blue = 0x00;
    strip_cyl4_white = 0x00;
  }
  else if(string_value >= 0 && string_value < 14)
  {
    // Orange
    strip_cyl4_red = 0xFF;
    strip_cyl4_green = 0x45;
    strip_cyl4_blue = 0x00;
    strip_cyl4_white = 0x00;
  }

  //for(int i=0; i<4; i++)
  strip_cyl_4.setPixelColor(0, strip_cyl4_red, strip_cyl4_green, strip_cyl4_blue, strip_cyl4_white);

  strip_cyl_4.show();


  char strip_cyl3_red = 0x00;
  char strip_cyl3_green = 0x00;
  char strip_cyl3_blue = 0x00;
  char strip_cyl3_white = 0x00;
  if(string_value >= 112 && string_value <= 127)
  {
    // Blue
    strip_cyl3_red = 0x00;
    strip_cyl3_green = 0x00;
    strip_cyl3_blue = 0xFF;
    strip_cyl3_white = 0x00;
  }
  else if(string_value >= 0 && string_value < 17)
  {
    // Blue
    strip_cyl3_red = 0x00;
    strip_cyl3_green = 0x00;
    strip_cyl3_blue = 0xFF;
    strip_cyl3_white = 0x00;
  }
  else if(string_value >= 17 && string_value < 46)
  {
    // Turqoise
    strip_cyl3_red = 0x40;
    strip_cyl3_green = 0xD0;
    strip_cyl3_blue = 0xE0;
    strip_cyl3_white = 0x00;
  }
  else if(string_value >= 46 && string_value < 49)
  {
    // White
    strip_cyl3_red = 0x00;
    strip_cyl3_green = 0x00;
    strip_cyl3_blue = 0x00;
    strip_cyl3_white = 0xFF;
  }
  else if(string_value >= 49 && string_value < 83)
  {
    // Red
    strip_cyl3_red = 0xFF;
    strip_cyl3_green = 0x00;
    strip_cyl3_blue = 0x00;
    strip_cyl3_white = 0x00;
  }
  else if(string_value >= 83 && string_value < 112)
  {
    // Orange
    strip_cyl3_red = 0xFF;
    strip_cyl3_green = 0x45;
    strip_cyl3_blue = 0x00;
    strip_cyl3_white = 0x00;
  }

  //for(int i=0; i<4; i++)
  strip_cyl_3.setPixelColor(0, strip_cyl3_red, strip_cyl3_green, strip_cyl3_blue, strip_cyl3_white);

  strip_cyl_3.show();

  char strip_cyl2_red = 0x00;
  char strip_cyl2_green = 0x00;
  char strip_cyl2_blue = 0x00;
  char strip_cyl2_white = 0x00;
  if(string_value >= 49 && string_value < 81)
  {
    // Blue
    strip_cyl2_red = 0x00;
    strip_cyl2_green = 0x00;
    strip_cyl2_blue = 0xFF;
    strip_cyl2_white = 0x00;
  }
  else if(string_value >= 81 && string_value < 103)
  {
    // Turqoise
    strip_cyl2_red = 0x40;
    strip_cyl2_green = 0xD0;
    strip_cyl2_blue = 0xE0;
    strip_cyl2_white = 0x00;
  }
  else if(string_value >= 103 && string_value < 106)
  {
    // White
    strip_cyl2_red = 0x00;
    strip_cyl2_green = 0x00;
    strip_cyl2_blue = 0x00;
    strip_cyl2_white = 0xFF;
  }
  else if(string_value >= 106 && string_value < 108)
  {
    // Red
    strip_cyl2_red = 0xFF;
    strip_cyl2_green = 0x00;
    strip_cyl2_blue = 0x00;
    strip_cyl2_white = 0x00;
  }
  else if(string_value >= 108 && string_value < 111)
  {
    // White
    strip_cyl2_red = 0x00;
    strip_cyl2_green = 0x00;
    strip_cyl2_blue = 0x00;
    strip_cyl2_white = 0xFF;
  }
  else if(string_value >= 111 && string_value <= 127)
  {
    // Red
    strip_cyl2_red = 0xFF;
    strip_cyl2_green = 0x00;
    strip_cyl2_blue = 0x00;
    strip_cyl2_white = 0x00;
  }
  else if(string_value > 0 && string_value <= 18)
  {
    // Red
    strip_cyl2_red = 0xFF;
    strip_cyl2_green = 0x00;
    strip_cyl2_blue = 0x00;
    strip_cyl2_white = 0x00;
  }
  else if(string_value > 18 && string_value < 49)
  {
    // Orange
    strip_cyl2_red = 0xFF;
    strip_cyl2_green = 0x45;
    strip_cyl2_blue = 0x00;
    strip_cyl2_white = 0x00;
  }

  strip_cyl_2.setPixelColor(0, strip_cyl2_red, strip_cyl2_green, strip_cyl2_blue, strip_cyl2_white);
  strip_cyl_2.show();

  char strip_cyl1_red = 0x00;
  char strip_cyl1_green = 0x00;
  char strip_cyl1_blue = 0x00;
  char strip_cyl1_white = 0x00;
  if(string_value >= 80 && string_value < 114)
  {
    // Blue
    strip_cyl1_red = 0x00;
    strip_cyl1_green = 0x00;
    strip_cyl1_blue = 0xFF;
    strip_cyl1_white = 0x00;
  }
  else if(string_value >= 114 && string_value <= 127)
  {
    // Turqoise
    strip_cyl1_red = 0x40;
    strip_cyl1_green = 0xD0;
    strip_cyl1_blue = 0xE0;
    strip_cyl1_white = 0x00;
  }
  else if(string_value >= 0 && string_value < 6)
  {
    // Turqoise
    strip_cyl1_red = 0x40;
    strip_cyl1_green = 0xD0;
    strip_cyl1_blue = 0xE0;
    strip_cyl1_white = 0x00;
  }
  else if(string_value >= 6 && string_value < 9)
  {
    // White
    strip_cyl1_red = 0x00;
    strip_cyl1_green = 0x00;
    strip_cyl1_blue = 0x00;
    strip_cyl1_white = 0xFF;
  }
  else if(string_value >= 9 && string_value < 13)
  {
    // Read
    strip_cyl1_red = 0xFF;
    strip_cyl1_green = 0x00;
    strip_cyl1_blue = 0x00;
    strip_cyl1_white = 0x00;
  }
  else if(string_value >= 13 && string_value < 16)
  {
    // White
    strip_cyl1_red = 0x00;
    strip_cyl1_green = 0x00;
    strip_cyl1_blue = 0x00;
    strip_cyl1_white = 0xFF;
  }
  else if(string_value >= 16 && string_value <= 50)
  {
    // Red
    strip_cyl1_red = 0xFF;
    strip_cyl1_green = 0x00;
    strip_cyl1_blue = 0x00;
    strip_cyl1_white = 0x00;
  }
  else if(string_value > 50 && string_value < 80)
  {
    // Orange
    strip_cyl1_red = 0xFF;
    strip_cyl1_green = 0x45;
    strip_cyl1_blue = 0x00;
    strip_cyl1_white = 0x00;
  }

  //for(int i=0; i<4; i++)
  strip_cyl_1.setPixelColor(0, strip_cyl1_red, strip_cyl1_green, strip_cyl1_blue, strip_cyl1_white);

  strip_cyl_1.show();

  char strip_piston_1_red = 0xFF;
  char strip_piston_1_green = 0x45;
  char strip_piston_1_blue = 0x00;
  for(int i=0; i<4; i++)
    strip_piston_1.setPixelColor(i, strip_piston_1_red, strip_piston_1_green, strip_piston_1_blue);
  strip_piston_1.show();

  char strip_piston_2_red = 0xFF;
  char strip_piston_2_green = 0x45;
  char strip_piston_2_blue = 0x00;
  for(int i=0; i<4; i++)
    strip_piston_2.setPixelColor(i, strip_piston_2_red, strip_piston_2_green, strip_piston_2_blue);
  strip_piston_2.show();
}

void setColor1(int R1, int G1, int Bl1, int W1)
{
#ifdef COMMON_ANODE1

  R1 = 255 - R1;
  G1 = 255 - G1;
  Bl1 = 255 - Bl1;
  W1 = 255 - W1 ;
#endif
  analogWrite(Red1, R1);
  analogWrite(Green1, G1);
  analogWrite(Blue1, Bl1);
  analogWrite(White1, W1);
}


void updateStringValue()
{
  //  Reading Pin Values
  State1 = !digitalRead(Pin1);
  State2 = !digitalRead(Pin2);
  State3 = !digitalRead(Pin3);
  State4 = !digitalRead(Pin4);
  State5 = !digitalRead(Pin5);
  State6 = !digitalRead(Pin6);
  State7 = !digitalRead(Pin7);
  State8 = !digitalRead(Pin8);

  ///  Defining Each Position " Only Even Ones "
  // #0
  if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
      && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 0;
  }

  // #1
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 1;
  }
  // #2
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 2;
  }
    // #3
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 3;
  }
  // #4
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 4;
  }
  // #5
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 5;
  }
  // #6
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 6;
  }
  // #7
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 7;
  }
  // #8
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 8;
  }
  // #9
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW )) {
    string_value = 9;
  }
  // #10
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 10;
  }
    // #11
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 11;
  }
  // #12
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 12;
  }
    // #13
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 13;
  }
  // #14
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 14;
  }
    // #15
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 15;
  }
  // #16
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 16;
  }
    // #17
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 17;
  }
  // #18
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 18;
  }
    // #19
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 19;
  }
  // #20
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 20;
  }
    // #21
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 21;
  }
  // #22
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 22;
  }
    // #23
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 23;
  }
  // #24
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 24;
  }
    // #25
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 25;
  }
  // #26
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 26;
  }
    // #27
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 27;
  }
  // #28
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 28;
  }
    // #29
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 29;
  }
  // #30
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 30;
  }
    // #31
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 31;
  }
  // #32
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 32;
  }
    // #33
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 33;
  }
  // #34
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 34;
  }
    // #35
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 35;
  }
  // #36
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 36;
  }
    // #37
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 37;
  }
  // #38
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 38;
  }
    // #39
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 39;
  }
  // #40
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 40;
  }
    // #41
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 41;
  }
  // #42
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 42;
  }
    // #43
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 43;
  }
  // #44
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 44;
  }
    // #45
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 45;
  }
  // #46
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 46;
  }
    // #47
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 47;
  }
  // #48
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 48;
  }
    // #49
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 49;
  }
  // #50
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 50;
  }
    // #51
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 51;
  }
  // #52
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 52;
  }
    // #53
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 53;
  }
  // #54
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 54;
  }
    // #55
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 55;
  }
  // #56
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 56;
  }
    // #57
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 57;
  }
  // #58
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 58;
  }
    // #59
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 59;
  }
  // #60
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 60;
  }
    // #61
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 61;
  }
  // #62
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 62;
  }
    // #63
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 63;
  }
  // #64
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 64;
  }
    // #65
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 65;
  }
  // #66
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 66;
  }
    // #67
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 67;
  }
  // #68
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 68;
  }
    // #69
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 69;
  }
  // #70
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 70;
  }
    // #71
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 71;
  }
  // #72
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 72;
  }
    // #73
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 73;
  }
  // #74
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 74;
  }
    // #75
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 75;
  }
  // #76
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 76;
  }
    // #77
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 77;
  }
  // #78
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 78;
  }
    // #79
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 79;
  }
  // #80
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 80;
  }
    // #81
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 81;
  }
  // #82
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 82;
  }
    // #83
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 83;
  }
  // #84
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 84;
  }
    // #85
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 85;
  }
  // #86
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 86;
  }
    // #87
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 87;
  }
  // #88
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 88;
  }
    // #89
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 89;
  }
  // #90
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 90;
  }
    // #91
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 91;
  }
  // #92
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 92;
  }
    // #93
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 93;
  }
  // #94
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 94;
  }
    // #95
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 95;
  }
  // #96
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 96;
  }
    // #97
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 97;
  }
  // #98
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 98;
  }
    // #99
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 99;
  }
  // #100
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 100;
  }
    // #101
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 101;
  }
  // #102
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 102;
  }
    // #103
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 103;
  }
  // #104
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 104;
  }
    // #105
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 105;
  }
  // #106
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 106;
  }
    // #107
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 107;
  }
  // #108
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 108;
  }
    // #109
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 109;
  }
  // #110
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 110;
  }
    // #111
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 111;
  }
  // #112
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    string_value = 112;
  }
    // #113
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 113;
  }
  // #114
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 114;
  }
    // #115
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 115;
  }
  // #116
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 116;
  }
    // #117
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 117;
  }
  // #118
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 118;
  }
    // #119
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 119;
  }
  // #120
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 120;
  }
    // #121
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 121;
  }
  // #122
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 122;
  }
    // #123
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 123;
  }
  // #124    b
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    string_value = 124;
  }
    // #125
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    string_value = 125;
  }
  // #126
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 126;
  }
    // #127
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    string_value = 127;
  }
  //char buffer[1000];
  //sprintf(buffer, "%d %d %d %d %d %d %d %d", State1, State2, State3, State4, State5, State6, State7, State8);
  //Serial.println(buffer);
  Serial.println(string_value);
  // Printing string_value Value to Serial Monitor
}

