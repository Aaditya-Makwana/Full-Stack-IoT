#include <WiFi.h>
#include <ModbusIP_ESP8266.h>
#include <WiFiUdp.h>

const char* ssid = "your_ssid";
const char* password = "your_password";
const int UDP_PORT = 4210;
const int SLAVE_ID = 1;

uint16_t INPUT_REG_VAL[] = {0, 0, 0, 0};
const int SERVER_HREG1 = 100;
const int SERVER_HREG2 = 101;
const uint16_t WRITE_VALUE1 = 1234;
const uint16_t WRITE_VALUE2 = 5678;

ModbusIP mb;
WiFiUDP udp;
IPAddress slaveIP;
bool slaveDiscovered = false;

void setup() {
  Serial.begin(115200);

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

  udp.begin(UDP_PORT);
  discoverSlave();
}

void loop() {
  if (!slaveDiscovered) {
    discoverSlave();
    delay(1000);
  } else {
    if (mb.isConnected(slaveIP)) {
      mb.readIreg(slaveIP, 1, INPUT_REG_VAL, 4, nullptr);
      printValues();
      delay(100);
    } else {
      mb.connect(slaveIP);
    }
    mb.task();
  }
  delay(10);
}

void discoverSlave() {
  Serial.println("Broadcasting for slave...");
  udp.beginPacket(IPAddress(255, 255, 255, 255), UDP_PORT);
  udp.write(SLAVE_ID);
  udp.endPacket();
  
  int packetSize = udp.parsePacket();
  if (packetSize) {
    char incomingPacket[255];
    int len = udp.read(incomingPacket, 255);
    if (len > 0) {
      incomingPacket[len] = 0;
    }
    slaveIP.fromString(incomingPacket);
    slaveDiscovered = true;
    Serial.print("Slave discovered at IP: ");
    Serial.println(slaveIP);
    mb.connect(slaveIP); 
  }
}

void printValues() {
  for (int i = 0; i < 3; i++) {
    Serial.print(INPUT_REG_VAL[i]);
    Serial.print(", ");
  }
  Serial.println(INPUT_REG_VAL[3]);
}
