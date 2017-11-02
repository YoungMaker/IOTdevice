
#include <SPI.h>
#include <PN532_SPI.h>
#include <PN532.h>
#include <NfcAdapter.h>

#define LED 8

PN532_SPI pn532spi(SPI, 10);
NfcAdapter nfc = NfcAdapter(pn532spi);

bool contact = false;
String lastUid = ""; //the last UID to be scanned, your current drink
String UID = "";

void setup() {
  // put your setup code here, to run once:
 Serial.begin(9600);
 pinMode(LED, OUTPUT);
 digitalWrite(LED, LOW);
 nfc.begin();
 handshake();
 digitalWrite(LED, HIGH);
}

void loop() {
  digitalWrite(LED, HIGH);
  if(nfc.tagPresent()){
    NfcTag tag = nfc.read();
    UID = tag.getUidString();
    // if tag is not previous tag
    if(UID != lastUid) {
      lastUid = UID; 
      Serial.print("AW");
      Serial.println(UID);
      digitalWrite(LED, LOW);
    }
  }
  delay(300);
}


void handshake() {
  byte inByte = 0;
  while(!contact) {
    Serial.println("AT");
    while(Serial.available() > 0) {
      inByte = Serial.read();
      if(inByte == 'A' && Serial.read() == 'T') {
        contact = true;
        delay(100);
        Serial.println("AN");
      }
    }
    delay(300);
  }
}

