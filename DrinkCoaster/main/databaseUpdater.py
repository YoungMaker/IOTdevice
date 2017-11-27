import time, RfidReader
from tagdb import TagDatabase
from dateutil.parser import parse

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

                print success
                if success >= 0:
                    print "tag " + read + " successfully added to database\n"

        elif tagType == RfidReader.TAG_TYPE_USER or tagType == RfidReader.TAG_TYPE_ADMIN:
            tagDatabase.printUserInfo(read)

            if askYesNo("Tag " + read + " user is already in the database, would you like to remove it?\n" ):
                if removeTag(read, RfidReader.TAG_TYPE_USER, tagDatabase, rfidReader) > 0:
                    print "Tag " + read + " successfully removed\n"

            elif askYesNo("Tag " + read + " user is already in the database, would you like to update it it?\n" ):
                if removeConsumedDrink(read, tagDatabase, rfidReader) > 0:
                    print "Drink successfully removed"

        elif tagType == RfidReader.TAG_TYPE_DRINK:
            tagDatabase.printDrinkInfo(read)

            if askYesNo("Tag " + read + " drink is already in the database, would you like to remove it?\n" ):
                if removeTag(read, RfidReader.TAG_TYPE_DRINK, tagDatabase, rfidReader) > 0:
                    print "Tag " +read + " successfully removed\n"

            #elif askYesNo("Tag " + read + " drink is already in the database, would you like to update it?\n" ):
                #todo: update drink tag using questions
                #print "todo: update drink tag using questions \n"


        print "Leaving update mode\n"
        rfidReader.leaveUpdateMode() #leave update mode so we can again scan tags freely
    print "Ok, returning to read mode\n"

def removeTag(tagId,tagType, tagDatabase, rfidReader):
    rfidReader.leaveUpdateMode() #unlock scanner
    print "Please present the tag you want to remove again"
    read = rfidReader.waitForTagRead(delay=0.3, timeout=200)

    if read != tagId:
        print "Correct tag was not scanned. Operation canceled \n"
        return INPUT_ERROR

    if tagType == RfidReader.TAG_TYPE_DRINK:
        print "OK, removing drink "
        tagDatabase.printDrinkInfo(tagId)
        return tagDatabase.removeDrink(tagId)
    elif tagType == RfidReader.TAG_TYPE_USER:
        print "OK, removing user "
        tagDatabase.printUserInfo(tagId)
        return tagDatabase.removeUser(tagId)



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
    name = raw_input("Enter the name of the user:\n")
    print "Ok, the user's name is " + name +"\n"

    dob = raw_input("Enter the users DOB in dd/mm/yyyy:\n")
    while True:
        try:
            dob = parse(dob, dayfirst=True)
        except ValueError:
            dob = raw_input("Incorrect date format. Please Enter the users DOB in dd/mm/yyyy:\n")
        else :
            break

    print "Ok, the users's date of birthday is  " + str(dob) +"\n"

    weight = raw_input("Enter the weight of the user, in Kg. Quantity < 0 will quit\n")
    while True:
        try:
            weight = int(weight)
        except ValueError:
            weight = raw_input("Please enter an integer value, qty < 0 to quit:\n")
        else:
            #user entered integer
            break

    if weight < 0:
        print "Operation cancelled\n"
        return INPUT_ERROR

    dose = raw_input("Enter the quantity of the drug, in milliliters that the user has currently consumed. Quantity < 0 will assume 0\n")
    while True:
        try:
            dose = int(dose)
        except ValueError:
            dose = raw_input("Please enter an integer value\n")
        else:
            # user entered integer
            break

    if dose < 0: dose = 0

    print "User \"" + name + "\", dob: " + str(dob) + ", weighing " + str(weight) + "kg, has consumed " + str(dose) + " mg/ml \n"

    if askYesNo("Is this correct?\n"):
       return tagDatabase.addUserTag(tagId, name, dob, weight, dose)

    print "Operation cancelled\n"
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
    rfidReader.leaveUpdateMode()  # leave update mode so we can again scan tags freely
    print "please present a valid admin user card\n"
    read = rfidReader.waitForTagRead(delay=0.03, timeout=200)

    tagType = tagDatabase.getTagType(read)
    if tagType == RfidReader.TAG_TYPE_ADMIN:
        print "admin card accepted. Adding new admin user. "
        if addUserTag(tagId, tagDatabase, rfidReader) > 0:
            if tagDatabase.addAdminPrivleges(tagId) > 0:
                print "Admin privileges added successfully\n"
                return TagDatabase.DB_COMPLETE
    else:
        print "non-admin card presented, operation canceled\n"

    rfidReader.enterUpdateMode()  # reenter update mode
    return INPUT_ERROR

def removeConsumedDrink(tagId, tagDatabase, rfidReader):
    rfidReader.leaveUpdateMode()  # leave update mode so we can again scan tags freely
    print "please present the drink you would like to remove from the user \n"
    read = rfidReader.waitForTagRead(delay=0.03, timeout=600)

    if not read:
        print "No tag presented. Exiting"
        return INPUT_ERROR

    tagType = tagDatabase.getTagType(read)
    if tagType == RfidReader.TAG_TYPE_DRINK:
        tagDatabase.printDrinkInfo(read)
        if askYesNo("Remove this drink?"):
            return tagDatabase.removeConsumedDrink(tagId, read)
    else:
        print "No drink tag presented, operation canceled."

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