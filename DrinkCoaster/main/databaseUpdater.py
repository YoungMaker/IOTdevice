import time, RfidReader

def updateMode(tagDatabase, rfidReader):
    if askYesNo("Would you like to enter update mode\n"):
        print "Scan Tag to update database"

        read = ''
        while not read:
            read = rfidReader.tagRead()
            time.sleep(.3)

        print "TAG READ: " + repr(read)
        tagType = tagDatabase.getTagType(read)

        rfidReader.enterUpdateMode() #lock the reader so it cannot spam us with tags

        if tagType == RfidReader.TAG_TYPE_NONE:
            if askYesNo("Tag " + read + " was not in the database. Would you like to add it?\n"):
                #todo: ask what kind of tag it should be and add it accordingly
                print "todo: ask what kind of tag it should be and add it accordingly \n"
                pass
        elif tagType == RfidReader.TAG_TYPE_USER or tagType == RfidReader.TAG_TYPE_ADMIN:
            tagDatabase.printUserInfo(read)
            if askYesNo("Tag " + read + " user is already in the database, would you like to update it?\n" ):
                #todo: update user tag using questions
                print "todo: update user tag using questions \n"
                pass
        elif tagType == RfidReader.TAG_TYPE_DRINK:
            #todo: print drink tag info
            if askYesNo("Tag " + read + " drink is already in the database, would you like to update it?\n" ):
                #todo: update drink tag using questions
                print "todo: update drink tag using questions \n"
                pass

        print "Leaving update mode\n"
        rfidReader.leaveUpdateMode() #leave update mode so we can again scan tags freely
    print "Ok, returning to read mode\n"

def addUserTag(tagDatabase, rfidReader):
    pass

def addDrinkTag(tagDatabase, rfidReader):
    pass


def askYesNo(msg):
    resp = raw_input(msg)
    while True:
        resp = resp.lower()
        if resp == "y" or resp == "yes":
            return True
        elif resp == "no" or resp == "n":
            return False
        else:
            resp = raw_input("Please enter Y or YES for yes, N or NO for No")