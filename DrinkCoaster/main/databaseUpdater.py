import time, RfidReader
from tagdb import TagDatabase

INPUT_ERROR = -2

def updateMode(tagDatabase, rfidReader):
    if askYesNo("Would you like to enter update mode\n"):
        print "Scan Tag to update database"

        read = rfidReader.waitForTagRead(delay=0.3, timeout=200)

        if read == '':
            print "Scan timed out, exiting update mode\n"
            return

        tagType = tagDatabase.getTagType(read)

        rfidReader.enterUpdateMode() #lock the reader so it cannot spam us with tag reads

        if tagType == RfidReader.TAG_TYPE_NONE: #if tag isn't in database
            if askYesNo("Tag " + read + " was not in the database. Would you like to add it?\n"):
                tagType = askTagType()
                success = - 1000
                if tagType == RfidReader.TAG_TYPE_DRINK:
                    success = addDrinkTag(read, tagDatabase, rfidReader)
                elif tagType == RfidReader.TAG_TYPE_USER:
                    success = addUserTag(read, tagDatabase, rfidReader)
                elif tagType == RfidReader.TAG_TYPE_ADMIN:
                    success = addAdminTag(read, tagDatabase, rfidReader)

                if success >= 0:
                    print "tag " + read + " successfully added to database\n"

        elif tagType == RfidReader.TAG_TYPE_USER or tagType == RfidReader.TAG_TYPE_ADMIN:
            tagDatabase.printUserInfo(read)
            if askYesNo("Tag " + read + " user is already in the database, would you like to update it?\n" ):
                #todo: update user tag using questions
                print "todo: update user tag using questions \n"
                pass
        elif tagType == RfidReader.TAG_TYPE_DRINK:
            tagDatabase.printDrinkInfo()
            if askYesNo("Tag " + read + " drink is already in the database, would you like to update it?\n" ):
                #todo: update drink tag using questions
                print "todo: update drink tag using questions \n"
                pass

        print "Leaving update mode\n"
        rfidReader.leaveUpdateMode() #leave update mode so we can again scan tags freely
    print "Ok, returning to read mode\n"

def askTagType():
    inpt = raw_input("What kind of tag should this be? 0 for user, 1 for drink, 2 for admin:\n")

    while True:
        try:
            inpt = int(inpt)
        except ValueError:
            inpt = raw_input("Please enter an integer value for tag type. 0 for user, 1 for drink, 2 for admin:\n")
        else:
            #user entered integer
            break

    if inpt == RfidReader.TAG_TYPE_DRINK:
        print "Drink tag chosen\n"
        return inpt
    elif inpt == RfidReader.TAG_TYPE_USER:
        print "User tag chosen\n"
        return inpt
    elif inpt == RfidReader.TAG_TYPE_ADMIN:
        print "Admin tag chosen\n"
        return inpt
    else:
        print "You did not make a valid choice. Exiting setup mode"
        return INPUT_ERROR

def addUserTag(tagId, tagDatabase, rfidReader):
    return INPUT_ERROR

def addDrinkTag(tagId, tagDatabase, rfidReader):
    name = raw_input("Enter the name of the drink:\n")
    print "Ok, the name is " + name +"\n"

    drug = raw_input("Enter the drug name in the drink:\n")
    print "Ok, the drug of choice is " + drug +"\n"

    qty = raw_input("Enter the quantity of the drink, in milliliters. Quantity < 0 will quit\n")
    while True:
        try:
            qty = int(qty)
        except ValueError:
            qty = raw_input("Please enter an integer value, qty < 0 to quit:\n")
        else:
            #user entered integer
            break

    if qty < 0:
        print "Operation cancelled\n"
        return INPUT_ERROR

    dose = raw_input("Enter the quantity of the drug, in milliliters. Quantity < 0 will quit\n")
    while True:
        try:
            dose = int(dose)
        except ValueError:
            dose = raw_input("Please enter an integer value, dose < 0 to quit:\n")
        else:
            # user entered integer
            break

    if dose < 0:
        print "Operation cancelled\n"
        return INPUT_ERROR

    print "Drink " + str(qty) + "ml \"" + name + "\" containing " + str(dose) + "mg/ml of \"" + drug + "\" \n"

    if askYesNo("Is this correct?\n"):
       return tagDatabase.addDrinkTag(tagId, name, drug, qty, dose)

    print "Operation cancelled\n"
    return INPUT_ERROR


def addAdminTag(tagId, tagDatabase, rfidReader):
    return INPUT_ERROR


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