import RfidReader, time

if __name__ == '__main__':
    #todo: open serial port and communicate with arduino
    reader = RfidReader.RfidReader("COM4")

    read = ''
    while True :

        while not read:
            read = reader.tagRead()
            time.sleep(.5)

        print "TAG READ: " + repr(read)
        read = ''
        time.sleep(1)
