import RfidReader, time, databaseUpdater
from tagdb import TagDatabase


def readMode(reader, db):
    read = ''
    while True :

        while not read:
            read = reader.tagRead()
            time.sleep(.5)

        if read == "00D077DE":  #hack exit tag for now.
            return -1

        print "TAG READ: " + repr(read)
        tagType = db.getTagType(read)
        if tagType ==  RfidReader.TAG_TYPE_USER:
            db.printUserInfo(read)
            print db.getUserName(read) + " is now the current user, entering drink mode \n"
            return read
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

def drinkMode(reader, db, user):

    read = ''


    drink = '' #current drink
    while True :

        while not read:
            read = reader.tagRead()
            time.sleep(.5)

        if read == "00D077DE":  #hack exit tag for now.
            return

        #print "TAG READ: " + repr(read)
        tagType = db.getTagType(read)
        if tagType ==  RfidReader.TAG_TYPE_USER:
            db.printUserInfo(read)
            print db.getUserName(read) + " is now the current drinker"
            user = read #set the current drinker
        if tagType == RfidReader.TAG_TYPE_ADMIN:
            db.printUserInfo(read)
            print "Admin card accepted\n"
            databaseUpdater.updateMode(db, reader)
        if tagType == RfidReader.TAG_TYPE_DRINK:
            db.printDrinkInfo(read)
            drink = read
            print db.getUserName(user) + " is currently drinking " + db.getDrinkName(drink)
        if tagType == RfidReader.TAG_TYPE_NONE:
            print "tag " + read + " is not in the database. Scan an admin tag to enter update mode if you wish to add it\n"
        if tagType == RfidReader.TAG_TYPE_CMPL:
            print db.getUserName(user) + " has finished consuming " + db.getDrinkName(drink)
            db.consumeDrink(user, drink)


        read = ''
        time.sleep(1)


if __name__ == '__main__':
    #open serial port and communicate with arduino
    comport = raw_input("enter the Serial port number\n")
    reader = RfidReader.RfidReader(comport)
    db = TagDatabase()
    seed_user = readMode(reader, db)
    if seed_user != -1:
        drinkMode(reader, db, seed_user)

    db.disconnect()
    reader.disconnect()