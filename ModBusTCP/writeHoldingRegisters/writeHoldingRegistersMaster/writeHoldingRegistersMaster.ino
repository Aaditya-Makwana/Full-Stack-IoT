#include <WiFi.h>
#include <ModbusIP_ESP8266.h>

const char* ssid = "your_ssid";
const char* password = "your_password";
IPAddress serverIP(192, 168, 0, 0); //Replace with the Slave IP

const int SERVER_HREG1 = 100; // First Holding Register address on server
const int SERVER_HREG2 = 101; // Second Holding Register address on server
const uint16_t WRITE_VALUE1 = 1234; // First value to write to Holding Register
const uint16_t WRITE_VALUE2 = 5678; // Second value to write to Holding Register

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

  mb.client();
  mb.connect(serverIP);
}

void loop() {
  if (mb.isConnected(serverIP)) {
    mb.writeHreg(serverIP, SERVER_HREG1, WRITE_VALUE1);
    Serial.println("Value 1234 written to Holding Register 100 on server.");

    mb.writeHreg(serverIP, SERVER_HREG2, WRITE_VALUE2);
    Serial.println("Value 5678 written to Holding Register 101 on server.");

    delay(100);
  } else {
    mb.connect(serverIP);
  }

  mb.task();
  delay(10);
}
