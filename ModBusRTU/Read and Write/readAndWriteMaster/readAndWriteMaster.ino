/*
Using serial communication to write a holding register inside the slave

RX and TX pins of one controller is connected to the opposite pin of the other controller, i.e,
RX (Master) -> TX (Slave)
TX (Master) -> RX (Slave)

GREENREG and REDREG are registers for external LEDs which we used for demonstration purposes.
They are NOT NECESSARY for the Modbus functionality

Refer to comments in the code for more details
*/

#include <ModbusRTU.h>

#define RX 13
#define TX 12
#define SLAVE_ID 1
#define GREENREG 5
#define REDREG 6

ModbusRTU mb;

uint16_t values[] = {0, 0, 0, 0};
uint16_t addr[] = {1, 2, 3, 4};

bool greenWriteTask = false;
bool redWriteTask = false;
bool readTask = false;

/*
The above task variables are necessary due to asynchronous nature of ModbusRTU. If you try to write
two mb.writeHreg() statements one after the other, only the first one gets executed

To avoid this, we only move on once all the commands are executed, for which the task variables are required
We assign these variables true inside the callback function, ensuring that the command has been executed
When all the commands are executed, we make them false once again, and the cycle repeats.
*/

void setup() {
  Serial.begin(9600, SERIAL_8N1);
  Serial2.begin(9600, SERIAL_8N1, RX, TX);
  mb.begin(&Serial2); //Initializes Modbus on Serial2 Channel
  mb.master(); //Tells the current device that it is the master
}

void loop() {
  mb.task(); //The magic function which handles all the communication

  if (!mb.slave()) {

    if(!greenWriteTask){
      mb.writeHreg(SLAVE_ID, GREENREG, values[2], cbWriteGreen);
    }

    if(greenWriteTask && !redWriteTask){
      mb.writeHreg(SLAVE_ID, REDREG, values[3], cbWriteRed);
    }

    if(greenWriteTask && redWriteTask && !readTask){
      mb.readIreg(SLAVE_ID, 1, values, 4, cbRead);
      //mb.readIreg(SLAVE_ID, STARTING_ADDRESS, ADDRESS_TO_STORE, NUMBER_OF_REGISTERS, CALLBACK_FUNC);
    }

    if(greenWriteTask && redWriteTask && readTask){
      Serial.println("LED and values updated");
      printValues();
      greenWriteTask = false;
      redWriteTask = false;
      readTask = false;
    }
  }
}

void printValues() {
  Serial.print("Values array: ");
  for (int i = 0; i < 3; i++) {
    Serial.print(values[i]);
    Serial.print(", ");
  }
  Serial.println(values[3]);
}

bool cbWriteGreen(Modbus::ResultCode event, uint16_t transactionId, void* data) {
  if (event == Modbus::EX_SUCCESS) {
    Serial.println("Green Write successful");
    greenWriteTask = true;
    return true;
  } else {
    Serial.print("Write failed with code: ");
    Serial.println(event);
    return false;
  }
}

bool cbWriteRed(Modbus::ResultCod e event, uint16_t transactionId, void* data) {
  if (event == Modbus::EX_SUCCESS) {
    Serial.println("Red Write successful");
    redWriteTask = true;
    return true;
  } else {
    Serial.print("Write failed with code: ");
    Serial.println(event);
    return false;
  }
}

bool cbRead(Modbus::ResultCode event, uint16_t transactionId, void* data) {
  if (event == Modbus::EX_SUCCESS) {
    Serial.println("Read successful");
    readTask = true;
    return true;
  } else {
    Serial.print("Read failed with code: ");
    Serial.println(event);
    return false;
  }
}