// THIS CODE IS DESIGNED TO BE USED IN CONJUCTION WITH THE TRD CUTAWAY
// 10K resistors for Encoder
// Last Revision = June 6 2016
//Any Questions Contact Nicholas Rivero riveronamech@gmail.com


// These pins are input pins and realte to the BOURNS Encoder Serial EAWOJ-B24-AEO128L
const int Pin1 = 30; // Encoder Digital Inputs 1-8
const int Pin2 = 32;   
const int Pin3 = 34;
const int Pin4 = 36;
const int Pin5 = 38;
const int Pin6 = 40;
const int Pin7 = 42;
const int Pin8 = 44;

// These pins are output pins and control an individual LED
const int Red1 = 2;      // Red LED CYL #1
const int Green1 =3;   // Green LED  CYL #1
const int Blue1 = 4;   // Blue LED CYL #1
const int White1 =5;   // White LED CYL #1
const int Fuel1  =6;   // Single BLUE LED FOR Fuel 

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

//                      ######        CYL #2      ###########
//float IntOn2 = 103;   // Intake LED cyl #2  on ( Deg )
//float IntOff2 = 203;   // Intake LED cyl #2 off ( Deg )
//float ComOn2 = 203;   // Compression LED cyl #2  on ( Deg )
//float ComOff2 = 287;   // Compression LED cyl #2 off ( Deg )
//float SparkOn2 = 287;
//float SparkOff2 = 293;
//float PowOn2 = 294;
//float PowOff2 = 11;
//float ExhOn2 = 11;    // Exhaust LED cyl #2 on ( Deg )
//float ExhOff2 = 103;    // Exhaust LED cyl #2 off ( Deg )
//float FuelOn2 = 345 ;   // Fuel LED cyl #2  on ( Deg )
//float FuelOff2 = 262;   // Fuel LED cyl #2 off ( Deg )

float TDCon = 160;       // Indicate TDC LED on the PCB board so you can set the motor to TDC then 


// Variables
int String = 0;  //Variable used to store position value, between 0 and 127

int State1 = 0;   // Variables representing high or low pin states
int State2 = 0;
int State3 = 0;
int State4 = 0;
int State5 = 0;
int State6 = 0;
int State7 = 0;
int State8 = 0; 
void setup() {
  
  // Defining previously declared pins on the arduino mega to be read as input and outputs.
  pinMode( Pin1, INPUT);
  pinMode( Pin2, INPUT);
  pinMode( Pin3, INPUT);
  pinMode( Pin4, INPUT);
  pinMode( Pin5, INPUT);
  pinMode( Pin6, INPUT);
  pinMode( Pin7, INPUT);
  pinMode( Pin8, INPUT);

  pinMode ( Red1, OUTPUT );
  pinMode ( Green1, OUTPUT );
  pinMode ( Blue1, OUTPUT );
  pinMode ( White1, OUTPUT );
  pinMode ( Fuel1, OUTPUT );
//
//  pinMode ( Red2, OUTPUT );
//  pinMode ( Green2, OUTPUT );
//  pinMode ( Blue2, OUTPUT );
//  pinMode ( Spark2 , OUTPUT );
//  pinMode ( TDCLED , OUTPUT );
  // Setting Serial Monitor Rate
  Serial.begin(9600);
}

void loop() {



  //  Reading Pin Values
  State1 = digitalRead(Pin1);
  State2 = digitalRead(Pin2);
  State3 = digitalRead(Pin3);
  State4 = digitalRead(Pin4);
  State5 = digitalRead(Pin5);
  State6 = digitalRead(Pin6);
  State7 = digitalRead(Pin7);
  State8 = digitalRead(Pin8);

  ///  Defining Each Position " Only Even Ones "
  // #0
  if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
      && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    String = 0;
  }

  // #1
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 1;
  }
  // #2
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 2;
  }
    // #3
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 3;
  }
  // #4
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 4;
  }
  // #5
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    String = 5;
  }
  // #6
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 6;
  }
  // #7
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 7;
  }
  // #8
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 8;
  }
  // #9
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW )) {
    String = 9;
  }
  // #10
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    String = 10;
  }
    // #11
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    String = 11;
  }
  // #12
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    String = 12;
  }
    // #13
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 13;
  }
  // #14
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 14;
  }
    // #15
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    String = 15;
  }
  // #16
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    String = 16;
  }
    // #17
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 17;
  }
  // #18
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 18;
  }
    // #19
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 19;
  }
  // #20
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 20;
  }
    // #21
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    String = 21;
  }
  // #22
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    String = 22;
  }
    // #23
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 23;
  }
  // #24
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 24;
  }
    // #25
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 25;
  }
  // #26
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    String = 26;
  }
    // #27
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    String = 27;
  }
  // #28
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    String = 28;
  }
    // #29
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 29;
  }
  // #30
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 30;
  }
    // #31
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 31;
  }
  // #32
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 32;
  }
    // #33
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 33;
  }
  // #34
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 34;
  }
    // #35
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 35;
  }
  // #36
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 36;
  }
    // #37
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 37;
  }
  // #38
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 38;
  }
    // #39
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 39;
  }
  // #40
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 40;
  }
    // #41
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 41;
  }
  // #42
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    String = 42;
  }
    // #43
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    String = 43;
  }
  // #44
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 44;
  }
    // #45
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 45;
  }
  // #46
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 46;
  }
    // #47
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 47;
  }
  // #48
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 48;
  }
    // #49
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 49;
  }
  // #50
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 50;
  }
    // #51
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    String = 51;
  }
  // #52
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 52;
  }
    // #53
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 53;
  }
  // #54
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 54;
  }
    // #55
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 55;
  }
  // #56
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 56;
  }
    // #57
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 57;
  }
  // #58
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 58;
  }
    // #59
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    String = 59;
  }
  // #60
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 60;
  }
    // #61
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 61;
  }
  // #62
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 62;
  }
    // #63
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 63;
  }
  // #64
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 64;
  }
    // #65
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 65;
  }
  // #66
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 66;
  }
    // #67
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    String = 67;
  }
  // #68
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 68;
  }
    // #69
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 69;
  }
  // #70
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 70;
  }
    // #71
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 71;
  }
  // #72
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 72;
  }
    // #73
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 73;
  }
  // #74
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 74;
  }
    // #75
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 75;
  }
  // #76
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 76;
  }
    // #77
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 77;
  }
  // #78
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 78;
  }
    // #79
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 79;
  }
  // #80
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 80;
  }
    // #81
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 81;
  }
  // #82
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 82;
  }
    // #83
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 83;
  }
  // #84
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 84;
  }
    // #85
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 85;
  }
  // #86
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 86;
  }
    // #87
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 87;
  }
  // #88
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    String = 88;
  }
    // #89
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    String = 89;
  }
  // #90
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    String = 90;
  }
    // #91
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    String = 91;
  }
  // #92
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    String = 92;
  }
    // #93
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    String = 93;
  }
  // #94
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    String = 94;
  }
    // #95
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    String = 95;
  }
  // #96
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 96;
  }
    // #97
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 97;
  }
  // #98
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 98;
  }
    // #99
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 99;
  }
  // #100
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 100;
  }
    // #101
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 101;
  }
  // #102
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    String = 102;
  }
    // #103
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    String = 103;
  }
  // #104
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 104;
  }
    // #105
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 105;
  }
  // #106
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == LOW) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 106;
  }
    // #107
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 107;
  }
  // #108
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 108;
  }
    // #109
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 109;
  }
  // #110
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    String = 110;
  }
    // #111
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == HIGH)) {
    String = 111;
  }
  // #112
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == HIGH)) {
    String = 112;
  }
    // #113
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    String = 113;
  }
  // #114
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    String = 114;
  }
    // #115
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == HIGH) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    String = 115;
  }
  // #116
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    String = 116;
  }
    // #117
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == HIGH) && (State8 == LOW)) {
    String = 117;
  }
  // #118
  else if ((State1 == HIGH) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 118;
  }
    // #119
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == HIGH) && (State7 == LOW) && (State8 == LOW)) {
    String = 119;
  }
  // #120
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 120;
  }
    // #121
  else if ((State1 == LOW) && (State2 == LOW) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 121;
  }
  // #122
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == LOW)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 122;
  }
    // #123
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == LOW) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 123;
  }
  // #124    b
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == HIGH)) {
    String = 124;
  }
    // #125
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == LOW) && (State8 == LOW)) {
    String = 125;
  }
  // #126
  else if ((State1 == LOW) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    String = 126;
  }
    // #127
  else if ((State1 == HIGH) && (State2 == HIGH) && (State3 == HIGH) && (State4 == HIGH)
           && (State5 == HIGH) && (State6 == LOW) && (State7 == HIGH) && (State8 == LOW)) {
    String = 127;
  }
  Serial.println(String);
  // Printing String Value to Serial Monitor



  //  //////////////LED #1 //////////
  // these colors are completly backwards to normal PWM techniques due to the use of a PNP transistor(A92-B331) instead of a NPN when pnp is on npn transistors are off. if you use a NPN LM 137 for current regulation in the future 0 will be off and 255 will be HIGH 
  if ((( String >= 0.35 * PowOn1 ) && ( String <= 0.35 * PowOff1))) { // note here the positon of powon1 from above to corelate the rotation to the cam
    setColor1(50,200,255,255); // (r,g,b) varry between 0-255, 0 on 
  }
  else if ((( String >= 0.35 * ExhOn1 ) || ( String <= 0.35 * ExhOff1))) {
    setColor1(0,255,255,255);

  }
  else if ((( String >= 0.35 * IntOn1 ) && ( String <= 0.35 * IntOff1))) {
    setColor1(255,255,0,255);
  }
  else if ((( String >= 0.35 * ComOn1 ) && ( String <= 0.35 * ComOff1))) {
    setColor1(255,25,50,255);
  }
  else  ((( String >+ 0.35 * SparkOn1 ) && ( String < 0.35 * SparkOff1))) {
    setColor1(255,255,255,0);
  }
  //  ////////////// LED #2 //////////
//
//  if ((( String > 0.35 * PowOn2 ) || ( String <= 0.35 * PowOff2))) {
//    setColor2(50,150,255,255);
//
//  }
//  else if ((( String >= 0.35 * ExhOn2 ) && ( String <= 0.35 * ExhOff2))) {
//    setColor2(0,255,255,255);
//
//  }
//  else if ((( String >= 0.35 * IntOn2 ) && ( String <= 0.35 * IntOff2))) {
//    setColor2(255,255,0,255);
//  }
//  else if ((( String >= 0.35 * ComOn2 ) && ( String <= 0.35 * ComOff2))) {
//    setColor2(255,25,0,255);
//  }
//  else if ((( String >= 0.35 * SparkOn2 ) && ( String < 0.35 * SparkOff2))) {
//    setColor2(255,255,255,0);
//  }



  //  //////////////FUEL LED #1 //////////

  if (( String <= 0.35 * FuelOn1 ) && ( String >= 0.35 * FuelOff1)) {
    digitalWrite( Fuel1, HIGH);
  }
  else {
    digitalWrite( Fuel1, LOW );
  }
//
//  //  //////////////FUEL LED #2 //////////
//
//  if (( String <= 0.35 * FuelOn2 ) && ( String >= 0.35 * FuelOff2)) {
//    digitalWrite( Spark2, HIGH);
//  }
//  else {
//    digitalWrite( Spark2, LOW );
//  }

  ////////////////// TDC LIGHT ///////////

//  if ( String == 1 ) {
//    digitalWrite( TDCLED, HIGH);
//  }
//  else {
//    digitalWrite( TDCLED, LOW );
//  }
//}

//This is a sub routine for the set color function so this code does not need to be copied into each level of if else statement// you could also maken an encoder lookup table so you can get rid of the massive cumbersum string statement// never got around to it.
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
//void setColor2(int R2, int G2, int B2, int W2)
//{
//#ifdef COMMON_ANODE2
//  R2 = 255 - R2;
//  G2 = 255 - G2;
//  B2 = 255 - B2;
//  W2 = 255 - W2;
//#endif
//  analogWrite(Red2, R2);
//  analogWrite(Green2, G2);
//  analogWrite(Blue2, B2);
//  analogWrite(Spark2, W2);


//}
}
