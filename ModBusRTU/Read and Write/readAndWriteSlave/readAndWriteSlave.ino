/*
Using serial communication to write a holding register inside the slave

RX and TX pins of one controller is connected to the opposite pin of the other controller, i.e,
RX (Master) -> TX (Slave)
TX (Master) -> RX (Slave)

GREENREG and REDREG are registers for external LEDs which we used for demonstration purposes.
They are NOT NECESSARY for the Modbus functionality

Similarly, POT_PIN_ONE ... are pins we used for an external device. Again, this is for demonstration
purposes and NOT NECESSARY for Modbus functionality

Refer to comments in the code for more details
*/


#include <ModbusRTU.h>

#define RX 13
#define TX 12
#define SLAVE_ID 1

#define POT_PIN_ONE 32
#define POT_PIN_TWO 33
#define SWITCH_ONE 4
#define SWITCH_TWO 5
#define LED_GREEN 22
#define LED_RED 23

#define GREENREG 5
#define REDREG 6

ModbusRTU mb;

uint16_t values[] = {0, 0, 0, 0};
uint16_t addr[] = {1, 2, 3, 4};

void setup() {
  pinMode(SWITCH_ONE, INPUT);
  pinMode(SWITCH_TWO, INPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  Serial.begin(9600, SERIAL_8N1);
  Serial2.begin(9600, SERIAL_8N1, RX, TX);
  mb.begin(&Serial2); //Initialize Modbus on Serial2 Channel
  mb.setBaudrate(9600);
  mb.slave(SLAVE_ID);
  for(int i = 0;i<4;i++){
    mb.addIreg(addr[i]);  //Assign register addr[i] to be an input register
  }
  mb.addHreg(GREENREG, 0);
  mb.addHreg(REDREG, 0); //Assign GREENREG and REDREG to be a holding register with inital value 0
}

void loop() {
  mb.task();
  yield();
  delay(100);

  values[0] = analogRead(POT_PIN_ONE);
  values[1] = analogRead(POT_PIN_TWO);

  if(digitalRead(SWITCH_ONE) == HIGH){
    values[2] = 1;
  }
  else{
    values[2] = 0;
  }

  if(digitalRead(SWITCH_TWO) == HIGH){
    values[3] = 1;
  }
  else{
    values[3] = 0;
  }

  for(int i = 0;i<4;i++){
    mb.Ireg(addr[i], values[i]); //Write values[i] on input register addr[i]
  }

  updateLedState();
  //printValues(); //printing just to confirm that registers are updated
  delay(100);
}

void printValues(){
  Serial.print("Values array : ");
  for(int i = 0;i<3;i++){
    Serial.print(mb.Ireg(addr[i]));
    Serial.print(", ");
  }
  Serial.println(mb.Ireg(addr[3]));
}

void updateLedState(){
  if(mb.Hreg(GREENREG) == 1){
    digitalWrite(LED_GREEN, HIGH);
  }
  else{
    digitalWrite(LED_GREEN, LOW);
  }

  if(mb.Hreg(REDREG) == 1){
    digitalWrite(LED_RED, HIGH);
  }
  else{
    digitalWrite(LED_RED, LOW);
  }
}