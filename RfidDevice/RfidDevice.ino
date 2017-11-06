
#include <SPI.h>
#include <PN532_SPI.h>
#include <PN532.h>
#include <NfcAdapter.h>

#define LED 8
#define MODE_HANDSHAKE 0
#define MODE_READ 1
#define MODE_UPDATE 2


PN532_SPI pn532spi(SPI, 10);
NfcAdapter nfc = NfcAdapter(pn532spi);

String lastUid = ""; //the last UID to be scanned, your current drink
String UID = "";
int mode = MODE_HANDSHAKE;
char recvCode[3]; 

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
  while(Serial.available() > 0) {
    recvCode[0] = Serial.read();
    recvCode[1] = Serial.read();
    recvCode[2] = Serial.read();
    if(recvCode[0] == 'A' && recvCode[1] == 'R') {
      if(recvCode[2] == 'U') {
        mode = MODE_UPDATE;
        Serial.println("ARU");
        digitalWrite(LED, LOW);
      }
      else if(recvCode[2] == 'X'){
        mode = MODE_READ;
        Serial.println("ARX");
        lastUid = ""; //reset duplicate prevention.
      }
      else {} //unexpected 3 input string received, do nothing 
    }
    else if(recvCode[0] == 'A' && recvCode[1] == 'T') {
      mode = MODE_HANDSHAKE;
      digitalWrite(LED, LOW);
      delay(200);
      recvCode[0] = 0;
      recvCode[1] = 0;
      recvCode[2] = 0;
      Serial.flush();
      handshake();
      
    }
    recvCode[0] = 0;
    recvCode[1] = 0;
    recvCode[2] = 0;
  }

  if(mode == MODE_READ) { //constantly sends new tag scans to server
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
  }
  if(mode == MODE_UPDATE){ //sends only the first scan to the server, until update mode is exited.
     digitalWrite(LED, LOW);
     if(nfc.tagPresent()){
        NfcTag tag = nfc.read();
        UID = tag.getUidString();
        if(UID == lastUid) {
          lastUid = ""; //clear it so we can only send it once
          Serial.print("AW");
          Serial.println(UID);
          digitalWrite(LED, HIGH);
      }
    }
  }
  delay(300);
}



void handshake() {
  while(mode == MODE_HANDSHAKE) {
    Serial.println("AT");
    while(Serial.available() > 0) {
      recvCode[0] = Serial.read();
      recvCode[1] = Serial.read();
      if(recvCode[0] == 'A' && recvCode[1] == 'T') { //read ready from server
        mode = MODE_READ; //transition mode from handshake to read mode
        delay(100);
        Serial.println("AN"); //send acknowledge to server
      }
      recvCode[0] = 0;
      recvCode[1] = 0;
    }
    delay(300);
  }
}

