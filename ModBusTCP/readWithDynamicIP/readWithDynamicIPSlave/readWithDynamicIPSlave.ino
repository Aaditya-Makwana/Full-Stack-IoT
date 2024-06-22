#include <WiFi.h>
#include <ModbusIP_ESP8266.h>
#include <WiFiUdp.h>

#define POT_PIN_ONE 32
#define POT_PIN_TWO 33
#define SWITCH_ONE 4
#define SWITCH_TWO 5
#define LED_GREEN 22
#define LED_RED 23

const char* ssid = "your_ssid";
const char* password = "your_password";
const int UDP_PORT = 4210;
const int SLAVE_ID = 1;

uint16_t INPUT_REG_ADDR[] = {1, 2, 3, 4};
uint16_t INPUT_REG_VAL[] = {0, 0, 0, 0};
const int SERVER_HREG1 = 100;
const int SERVER_HREG2 = 101;

ModbusIP mb;
WiFiUDP udp;

void setup() {
  Serial.begin(115200);

  pinMode(SWITCH_ONE, INPUT);
  pinMode(SWITCH_TWO, INPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  mb.server();
  mb.addHreg(SERVER_HREG1, 0); 
  mb.addHreg(SERVER_HREG2, 0); 

  for (int i = 0; i < 4; i++) {
    mb.addIreg(INPUT_REG_ADDR[i], 0);
  }

  udp.begin(UDP_PORT);
}

void loop() {
  mb.task();

  updateValues();
  updateRegisters();

  int packetSize = udp.parsePacket();
  if (packetSize) {
    char incomingPacket[255];
    int len = udp.read(incomingPacket, 255);
    if (len > 0) {
      incomingPacket[len] = 0;
    }

    if (incomingPacket[0] == SLAVE_ID) {
      udp.beginPacket(udp.remoteIP(), udp.remotePort());
      udp.print(WiFi.localIP().toString());
      udp.endPacket();
      Serial.print("Responded to master with IP: ");
      Serial.println(WiFi.localIP());
    }
  }

  delay(100);
}

void updateValues(){
  INPUT_REG_VAL[0] = analogRead(POT_PIN_ONE);
  INPUT_REG_VAL[1] = analogRead(POT_PIN_TWO);
  INPUT_REG_VAL[2] = digitalRead(SWITCH_ONE);
  INPUT_REG_VAL[3] = digitalRead(SWITCH_TWO);
}

void updateRegisters(){
  for(int i = 0;i<4;i++){
    mb.Ireg(INPUT_REG_ADDR[i], INPUT_REG_VAL[i]);
  }
}
