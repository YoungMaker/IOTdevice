import sqlite3, RfidReader

class TagDatabase:

    db = None

    def __init__(self):
        global db
        #connect to database file
        db = sqlite3.connect("drink.db")


    def getTagType(self, tagId):
        global db
        cursor = db.cursor()
        cursor = cursor.execute("SELECT type FROM tags WHERE tag=?", (tagId,))
        tagType = cursor.fetchone()
        if tagType is None:
            return RfidReader.TAG_TYPE_NONE
        else: return tagType[0]

    def printUserInfo(self, tagId): # on;ly execute this with a user tag
        global db
        cursor = db.cursor()
        cursor = cursor.execute("SELECT name, dob, weight, dose FROM users WHERE tag=?", (tagId,))
        user = cursor.fetchone()
        if not (user is None):
            #print user
            print "Name: " + (user[0]) + ", Dob: " + user[1].replace("\\\\", "\\") + ", Weight: " + str(user[2]) + " Kg, " + "Has consumed: " + str(user[3]) + " ml\n"

    def disconnect(self):
        self.db.close()