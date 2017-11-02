import RfidReader, time

if __name__ == '__main__':
    #todo: open serial port and communicate with arduino
    reader = RfidReader.RfidReader("/dev/ttyACM0")

    read = False
    while(True):
        
        while not read:
            read = reader.tagRead()
            time.sleep(.5)

        print "TAG READ: " + repr(read)
        read = False
        time.sleep(1)
