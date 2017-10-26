import RfidReader, time

if __name__ == '__main__':
    #todo: open serial port and communicate with arduino
    reader = RfidReader.RfidReader("COM4")

    while(True):
        while not reader.tagRead() :
            time.sleep(.3)

        print "TAG READ"
        time.sleep(1)
