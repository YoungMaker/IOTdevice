import RfidReader, time
from tagdb import TagDatabase

if __name__ == '__main__':
    #todo: open serial port and communicate with arduino
    reader = RfidReader.RfidReader("COM4")
    db = TagDatabase()

    read = ''
    while True :

        while not read:
            read = reader.tagRead()
            time.sleep(.5)

        print "TAG READ: " + repr(read)
        print db.getTagType(read)
        read = ''
        time.sleep(1)
    db.disconnect()