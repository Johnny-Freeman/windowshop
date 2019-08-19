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
const int neoPin1 = 15;
const int neoPin2 = 15;
const int neoPin3 = 15;
const int neoPin4 = 15;

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
  pinMode( neoPin1, OUTPUT);
  pinMode( neoPin2, OUTPUT);
  pinMode( neoPin3, OUTPUT);
  pinMode( neoPin4, OUTPUT);
}

// Variables representing high or low pin states
  //Old-way
int State1 = 0;
int State2 = 0;
int State3 = 0;
int State4 = 0;
int State5 = 0;
int State6 = 0;
int State7 = 0;
int State8 = 0;
 
int encodeState[8];

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
  delay(1000);

  
}
