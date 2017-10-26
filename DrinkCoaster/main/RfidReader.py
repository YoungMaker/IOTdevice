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
        print("CLIENT READY\n")

    def tagRead(self):
        #wait for new serial information
        self.port.flush() #buffer is not getting flushed
        time.sleep(0.01)
        while self.port.in_waiting < 4:
            pass
        rcv = self.port.read(4)
        print repr(rcv) + '\n'
        if rcv == "AW":
            print self.port.readline() + '\n'
            return True
        elif not ( rcv == "AN\r\n"):
            print "HEARTBEAT LOST"
            return False
        else:
            return False


