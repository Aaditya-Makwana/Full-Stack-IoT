#include <WiFi.h>
#include <ModbusIP_ESP8266.h>

const char* ssid = "your_ssid";
const char* password = "your_password";

const int SERVER_HREG1 = 100;
const int SERVER_HREG2 = 101;

ModbusIP mb;

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  // Initialize Modbus server and add Holding Registers
  mb.server();
  mb.addHreg(SERVER_HREG1, 0); // Initialize first Holding Register with 0
  mb.addHreg(SERVER_HREG2, 0); // Initialize second Holding Register with 0
}

void loop() {
  mb.task();

  uint16_t value1 = mb.Hreg(SERVER_HREG1);
  uint16_t value2 = mb.Hreg(SERVER_HREG2);
  printHoldingRegisterValues(value1, value2);

  delay(100);
}

void printHoldingRegisterValues(uint16_t value1, uint16_t value2) {
  Serial.print("Received value in Holding Register 100: ");
  Serial.println(value1);
  Serial.print("Received value in Holding Register 101: ");
  Serial.println(value2);
}
