import RfidReader, time

if __name__ == '__main__':
    #todo: open database connection and interface
    reader = RfidReader.RfidReader("COM4")

    read = ''
    while True :

        while not read:
            read = reader.tagRead()
            time.sleep(.5)

        print "TAG READ: " + repr(read)
        read = ''
        time.sleep(1)
