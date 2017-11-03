import sqlite3

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
            return -1
        else: return tagType[0]

    def disconnect(self):
        self.db.close()