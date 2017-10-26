
#include <SPI.h>
#include <PN532_SPI.h>
#include <PN532.h>
#include <NfcAdapter.h>

PN532_SPI pn532spi(SPI, 10);
NfcAdapter nfc = NfcAdapter(pn532spi);

bool contact = false;

void setup() {
  // put your setup code here, to run once:
 Serial.begin(9600);
 pinMode(13, OUTPUT);
 digitalWrite(13, LOW);
 nfc.begin();
 handshake();
}

void loop() {
  if(nfc.tagPresent()){
    NfcTag tag = nfc.read();
    Serial.print("AW");
    Serial.println(tag.getUidString());
  }
  else {
    Serial.println("AN");
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
        digitalWrite(13, HIGH);
        contact = true;
      }
    }
    delay(300);
  }
}

