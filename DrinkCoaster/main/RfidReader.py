import serial, time

TAG_TYPE_USER = 0
TAG_TYPE_DRINK = 1
TAG_TYPE_NONE = -1
TAG_TYPE_ADMIN = 2

class RfidReader:

    port = None

    def __init__(self, COM, dataRate=9600):
        #todo, open serial port, handshake with client.

        self.port = serial.Serial(COM, dataRate)
        self.handshake(self.port)
        

    def handshake(self, port):
        servRdy = False
        devRdy = False
        print "SERV NOT READY, WAITING FOR AT"
        # waits for input on serial port such that input is AT
        while not servRdy:
            while port.in_waiting < 4:
                pass
            rcv = port.readline()
            if rcv == "AT\r\n":
                print "SERV READY, AT RCV\n"
                servRdy = True
            else:
                # print "AT INCORRECT, RCV  " + repr(rcv) + "\n"
                pass
            time.sleep(0.1)
            # server is ready
        self.port.write("AT") #send ready to IOT device
        time.sleep(0.1)
        port.reset_output_buffer()
        port.reset_input_buffer()
        time.sleep(0.3)
        while not devRdy:
            if port.in_waiting >= 2:
                port.readline() #ignore first line, carry over from last AT sent
                recv = port.read(2)
                if recv == "AT":
                    print "DEVICE DID NOT RCV AT, SERV STILL RDY"
                    self.port.write("AT")  # send ready to IOT device again
                elif recv == "AN":
                    print "DEVICE RDY, RCV AT"
                    devRdy = True
                else:
                    print "DID NOT RECV AT, DEVICE UNREADY, RESTART HANDSHAKE"
                    self.handshake(port)
                time.sleep(0.1)

        time.sleep(.5)
        self.port.reset_input_buffer()
		
        
    def tagRead(self):
        if self.port.in_waiting >= 4:
            #a new serial message has come through
            pre = self.port.read(2) #read the preamble
            rest =  self.port.readline() #read the rest of the message
            if pre == "AW": #if the preamble is a tag read
                rest = rest.replace("\r","") #remove whitespace chars
                rest = rest.replace("\n","")
                rest = rest.replace(" ", "")
                return rest #rest contains tag UID string, minus any terminating chars
            elif pre == "AT":
                print "DEVICE RESET, RESTART HANDSHAKE"
                self.handshake(self.port)
            else:
                #something other than a tag preamble was received. Ignore it
                #print "RECV: " + repr(pre + rest) + "\n"
                return ""
        else:
            return ""

    def enterUpdateMode(self):
        self.port.write("ARU")
        time.sleep(0.1)
        devRdy = False
        while not devRdy:
            if self.port.in_waiting >= 2:
                pre = self.port.read(2)  # read the preamble
                rest = self.port.readline()  # read the rest of the message

                rest = rest.replace("\r","") #remove whitespace chars
                rest = rest.replace("\n","")
                rest = rest.replace(" ", "")
                if pre == "AT":
                    print "DEVICE RESET, RESTART HANDSHAKE"
                    self.handshake(self.port)
                elif pre == "AR":
                    if rest == "U":
                        print "DEVICE IN UPDATE MODE, RCV ACK"
                        devRdy = True
                    else:
                        print "DEVICE WRONG MODE, RESEND COMMAND"
                else:
                  #something other than a tag preamble was received. Ignore it
                  pass
            self.port.write("ARU") #retry
            time.sleep(0.2)


    def leaveUpdateMode(self):
        self.port.write("ARX")
        time.sleep(0.1)
        devRdy = False
        while not devRdy:
            if self.port.in_waiting >= 2:
                pre = self.port.read(2)  # read the preamble
                rest = self.port.readline()  # read the rest of the message

                rest = rest.replace("\r", "")  # remove whitespace chars
                rest = rest.replace("\n", "")
                rest = rest.replace(" ", "")
                if pre == "AT":
                    print "RECIVE AT, DEVICE RESET, RESTART HANDSHAKE"
                    self.handshake(self.port)
                elif pre == "AR":
                    if rest == "X":
                        print "DEVICE IN READ TAG MODE, RCV ACK"
                        devRdy = True
                    else:
                        print "DEVICE WRONG MODE, RESEND COMMAND"
                else:
                    # something other than a tag preamble was received. Ignore it
                    pass
            self.port.write("ARX")  # retry
            time.sleep(0.2)


