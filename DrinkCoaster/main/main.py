import RfidReader, time, databaseUpdater
from tagdb import TagDatabase


if __name__ == '__main__':
    #todo: open serial port and communicate with arduino
    comport = raw_input("enter the Serial port number\n")
    reader = RfidReader.RfidReader(comport)
    db = TagDatabase()

    read = ''
    while True :

        while not read:
            read = reader.tagRead()
            time.sleep(.5)

        if read == "00D077DE":  #hack exit tag for now.
            break

        print "TAG READ: " + repr(read)
        tagType = db.getTagType(read)
        if tagType ==  RfidReader.TAG_TYPE_USER:
            db.printUserInfo(read)
        if tagType == RfidReader.TAG_TYPE_ADMIN:
            db.printUserInfo(read)
            print "Admin card accepted\n"
            databaseUpdater.updateMode(db, reader)
        if tagType == RfidReader.TAG_TYPE_DRINK:
            db.printDrinkInfo(read)
        if tagType == RfidReader.TAG_TYPE_NONE:
            print "tag " + read + " is not in the database. Scan an admin tag to enter update mode if you wish to add it\n"


        read = ''
        time.sleep(1)

    db.disconnect()
    reader.disconnect()