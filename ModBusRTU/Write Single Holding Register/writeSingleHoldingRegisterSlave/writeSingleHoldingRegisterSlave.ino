#include <ModbusRTU.h>

#define RX 13
#define TX 12
#define HREG 1
#define SLAVE_ID 1

ModbusRTU mb;

void setup() {
  Serial.begin(9600);
  Serial2.begin(9600, SERIAL_8N1, RX, TX);
  mb.begin(&Serial2);
  mb.setBaudrate(9600);
  mb.slave(SLAVE_ID);
  mb.addHreg(HREG, 0);
}

uint16_t read_value = 0;

void loop() {
  mb.task();

  read_value = mb.Hreg(HREG);
  Serial.print("Reading the value of holding register : ");
  Serial.println(read_value);

  delay(100);
}
