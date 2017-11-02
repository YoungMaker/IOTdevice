import serial, time

class RfidReader:

    port = None

    def __init__(self, COM, dataRate=9600):
        #todo, open serial port, handshake with client.
        self.port = serial.Serial(COM, dataRate)
        rdy = False
        print "DEVICE NOT READY, WAITING FOR AT"
        #waits for input on serial port such that input is AT
        while not rdy:
            while self.port.in_waiting < 4:
                pass
            rcv = self.port.readline()
            if rcv == "AT\r\n":
                print "SERVER READY, AT RCV\n"
                rdy = True
                break
            else:
                print "AT INCORRECT, RCV " + repr(rcv) + "\n"
            time.sleep(0.01)
        #server is ready
        self.port.write("AT") #send ready to IOT device
	if self.port.in_waiting >= 2:
            print self.port.read(2) + " HS\n"
            #if self.port.read(4) == "AT":
             #   print "DEVICE DID NOT RCV AT"
        time.sleep(.5)
        self.port.reset_input_buffer()
        
        
		
        
    def tagRead(self):
        if self.port.in_waiting >= 4:
            #a new serial message has come through
            pre = self.port.read(2) #read the preamble
            rest =  self.port.readline() + '\n' #read the rest of the message
            if pre == "AW": #if the preamble is a tag read
                rest = rest.replace("\r","") #remove whitespace chars
                rest = rest.replace("\n","")
                rest = rest.replace(" ", "")
                return rest #rest contains tag UID string, minus any terminating chars
            else:
                #something other than a tag preamble was received. Ignore it
                #print "RECV: " + repr(pre + rest) + "\n"
                return False
        else:
            return False
