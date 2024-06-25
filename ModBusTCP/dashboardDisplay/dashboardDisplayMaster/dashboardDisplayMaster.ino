//YET TO IMPLEMENT AUTO-REFRESH

#include <WiFi.h>
#include <ModbusIP_ESP8266.h>
#include <WiFiUdp.h>
#include <WebServer.h>

const char* ssid = "your_ssid";
const char* password = "your_password";
const int UDP_PORT = 4210;
const int SLAVE_ID = 1;

uint16_t INPUT_REG_VAL[] = {0, 0, 0, 0};

ModbusIP mb;
WiFiUDP udp;
IPAddress slaveIP;
bool slaveDiscovered = false;
WebServer server(80); // Create a web server on port 80

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

  server.on("/", handleRoot);
  server.onNotFound(handleNotFound);
  server.begin();
  Serial.println("Web server started.");

  discoverSlave();
}

void loop() {
  if (!slaveDiscovered) {
    discoverSlave();
    delay(1000);
  } else {
    if (mb.isConnected(slaveIP)) {
      mb.readIreg(slaveIP, 1, INPUT_REG_VAL, 4, nullptr);
      delay(100);
    } else {
      mb.connect(slaveIP);
    }
    mb.task();
  }
  
  server.handleClient();
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

void handleRoot() {
  //HTML code here, yet to be updated
}

void handleNotFound() {
  server.send(404, "text/plain", "404: Not found");
}
