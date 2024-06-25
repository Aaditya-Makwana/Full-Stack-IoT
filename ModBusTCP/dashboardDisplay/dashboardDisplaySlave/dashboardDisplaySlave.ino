#include <WiFi.h>
#include <ModbusIP_ESP8266.h>
#include <WiFiUdp.h>

#define POT_ONE 33
#define POT_TWO 32
#define SWITCH_ONE 4
#define SWITCH_TWO 5
// #define GREEN_LED 22
// #define RED_LED 23

const char* ssid = "your_ssid";
const char* password = "your_password";
const int UDP_PORT = 4210;
const int SLAVE_ID = 1;

uint16_t INPUT_REG_ADDR[] = {1, 2, 3, 4};
uint16_t INPUT_REG_VAL[] = {0, 0, 0, 0};
// const int GREEN_REG = 5;
// const int RED_REG = 6;

ModbusIP mb;
WiFiUDP udp;

void setup() {
  Serial.begin(115200);

  pinMode(SWITCH_ONE, INPUT);
  pinMode(SWITCH_TWO, INPUT);

//   pinMode(GREEN_LED, OUTPUT);
//   pinMode(RED_LED, OUTPUT);

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
//   mb.addHreg(GREEN_REG, 0); 
//   mb.addHreg(RED_REG, 0); 

  for (int i = 0; i < 4; i++) {
    mb.addIreg(INPUT_REG_ADDR[i], 0);
  }

  udp.begin(UDP_PORT);
}

void loop() {
  mb.task();

  updateValues();
//   updateLED();

  // Update input registers
  for (int i = 0; i < 4; i++) {
    mb.Ireg(INPUT_REG_ADDR[i], INPUT_REG_VAL[i]);
  }

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

  delay(1000);
}

void updateValues(){
  INPUT_REG_VAL[0] = analogRead(POT_ONE);
  INPUT_REG_VAL[1] = analogRead(POT_TWO);

  if(digitalRead(SWITCH_ONE) == HIGH){
    INPUT_REG_VAL[2] = 1;
  }
  else{
    INPUT_REG_VAL[2] = 0;
  }
  
  if(digitalRead(SWITCH_TWO) == HIGH){
    INPUT_REG_VAL[3] = 1;
  }
  else{
    INPUT_REG_VAL[3] = 0;
  }
}

// void updateLED(){
//   if(mb.Hreg(GREEN_REG) == 1){
//     digitalWrite(GREEN_LED, HIGH);
//   }
//   else{
//     digitalWrite(GREEN_LED, LOW);
//   }

//   if(mb.Hreg(RED_REG) == 1){
//     digitalWrite(RED_LED, HIGH);
//   }
//   else{
//     digitalWrite(RED_LED, LOW);
//   }
// }