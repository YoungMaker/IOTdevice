import sqlite3, RfidReader

DB_COMPLETE = 0
DB_ERROR = -1

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

    def printUserInfo(self, tagId): # only execute this with a user tag
        global db
        cursor = db.cursor()
        try:
            cursor = cursor.execute("SELECT name, dob, weight, dose FROM users WHERE tag=?", (tagId,))
            user = cursor.fetchone()
            if not (user is None):
                #print user
                print "Name: " + (user[0]) + ", Dob: " + user[1].replace("\\\\", "\\") + ", Weight: " + str(user[2]) + " Kg, " + "Has consumed: " + str(user[3]) + " ml\n"
            else:
                print "Query returned empty list\n"
                return DB_ERROR
        except sqlite3.IntegrityError:
            print "Database Integrity error"
            return DB_ERROR
        except sqlite3.DatabaseError as e:
            print "Database error: " +  str(e) + "\n"
            return DB_ERROR

        return DB_COMPLETE


    def printDrinkInfo(self, tagId): # only execute this with a user tag
        global db
        cursor = db.cursor()
        try:
            cursor = cursor.execute("SELECT name, drug, qty, dose FROM drinks WHERE tag=?", (tagId,))
            drink = cursor.fetchone()
            if not (drink is None):
                #print user
                print "Drink " + str(drink[2]) + "ml \"" + drink[0] + "\" containing " + str(drink[3]) + "mg/ml of \"" + drink[1] + "\" \n"
            else:
                print "Query returned empty list\n"
                return DB_ERROR
        except sqlite3.IntegrityError:
            print "Database Integrity error"
            return DB_ERROR
        except sqlite3.DatabaseError as e:
            print "Database error: " +  str(e) + "\n"
            return DB_ERROR

        return DB_COMPLETE

    def insertIntoTagsTable(self, tagId, type): #DO Not use, rollbacks do not work if subsequent query fails
        global db
        cursor = db.cursor()
        try: #note that a tag MUST be inserted into the tags table before the drinks table
            cursor.execute("INSERT INTO tags (tag, type) VALUES(?,?)", (tagId, RfidReader.TAG_TYPE_DRINK))
            db.commit()
        except sqlite3.IntegrityError:
            print "Exact tag is already in database\n"
            db.rollback()
            return DB_ERROR
        except sqlite3.DatabaseError as e:
            # Roll back any change if something goes wrong
            print "Database error: " +  str(e) + "\n"
            db.rollback()
            return DB_ERROR

        return DB_COMPLETE


    def addDrinkTag(self, tagId, name, drug, qty, dose):
        global db
        cursor = db.cursor()
        try:
            qty = int(qty)
            dose = int(dose)
        except ValueError:
            print "Incorrectly formatted insert into drinks table. Qty and Dose should be integers"
            return DB_ERROR

        try: #note that a tag MUST be inserted into the tags table before the drinks table
            cursor.execute("INSERT INTO tags (tag, type) VALUES(?,?)", (tagId, RfidReader.TAG_TYPE_DRINK))
            cursor.execute("INSERT INTO drinks(tag, name, drug, qty, dose) VALUES(?,?,?,?,?)", (tagId, name, drug, qty, dose))

            db.commit()
        except sqlite3.IntegrityError:
            print "Exact drink is already in database\n"
            db.rollback()
            return DB_ERROR
        except sqlite3.DatabaseError as e:
            # Roll back any change if something goes wrong
            print "Database error: " +  str(e) + "\n"
            db.rollback()
            return DB_ERROR

        return DB_COMPLETE


    def addUserTag(self, tagId, name, dob, weight, dose):
        global db
        cursor = db.cursor()
        try:
            dose = int(dose)
            weight = int(weight)
        except ValueError:
            print "Incorrectly formatted insert into users table. Weight and dose should be integers"
            return DB_ERROR

        try:  # note that a tag MUST be inserted into the tags table before the drinks table
            cursor.execute("INSERT INTO tags (tag, type) VALUES(?,?)", (tagId, RfidReader.TAG_TYPE_USER))
            cursor.execute("INSERT INTO users(tag, name, dob, weight, dose) VALUES(?,?,?,?,?)",
                               (tagId, name, dob, weight, dose))
            db.commit()
        except sqlite3.IntegrityError:
            print "Exact user is already in database\n"
            db.rollback()
            return DB_ERROR
        except sqlite3.DatabaseError as e:
            # Roll back any change if something goes wrong
            print "Database error: " + str(e) + "\n"
            db.rollback()
            return DB_ERROR

        return DB_COMPLETE


    def disconnect(self):
        global db
        if db is not None:
            print "database closed\n"
            db.close()