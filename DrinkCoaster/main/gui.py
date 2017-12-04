from Tkinter import *  #import * for now todo: change import to only the things we need
import tkMessageBox
import ttk as ttk
import RfidReader
from tagdb import TagDatabase

NOT_CONNECTED = -1
READ_MODE = 0
DRINK_MODE =1
UPDATE_MODE = 2


def pollReader():
    global user, state
    if state == READ_MODE:
        read = rfidReader.waitForTagRead(delay=0.001, timeout=10)
        if read:
            mf.tagRead(read)
            tagType = db.getTagType(read)
            if tagType == RfidReader.TAG_TYPE_DRINK:
                sf.setSidePanelDrink(read, db.getDrinkInfo(read))
                drink = read
                #user = ""
            elif tagType == RfidReader.TAG_TYPE_USER:
                sf.setSidePanelUser(read, db.getUserInfo(read))
                user = read
                drink = ""
            elif tagType == RfidReader.TAG_TYPE_ADMIN:
                #sf.setSidePanelUser(db.getUserInfo(read), True)
                user = ""
                enterUpdateMode()
        mf.after(100, pollReader) #re-poll the rfid reader in 100 milliseconds

def connect(COMPORT):
    global rfidReader, state
    rfidReader.connect(COMPORT)
    state = READ_MODE
    mf.setConnected()
    mf.after(200, pollReader) #poll the rfid reader in 200 milliseconds

def enterUpdateMode():
    global state
    if tkMessageBox.askquestion(title="admin mode", message="Would you like to enter admin mode?")  == 'yes':
        mf.setMainText("Scan Tag to Update Database")
        sf.clearEntry()
        state = UPDATE_MODE
        updateMode()

def exitUpdateMode():
    global state
    state = READ_MODE
    mf.setMainText("Now waiting for tag read")
    rfidReader.leaveUpdateMode()

def updateMode():
    global read
    read = rfidReader.waitForTagRead(delay=0.001, timeout=10)
    if read:
        mf.tagRead(read)
        tagType = db.getTagType(read)
        if tagType == RfidReader.TAG_TYPE_DRINK:
            sf.setSidePanelDrink(read, db.getDrinkInfo(read))
            sf.enterAdminMode()
            rfidReader.enterUpdateMode()
        elif tagType == RfidReader.TAG_TYPE_USER:
            sf.setSidePanelUser(read, db.getUserInfo(read))
            sf.enterAdminMode()
            rfidReader.enterUpdateMode()
        elif tagType == RfidReader.TAG_TYPE_ADMIN:
            #sf.setSidePanelUser(db.getUserInfo(read))
            sf.exitAdminMode()
        elif tagType == RfidReader.TAG_TYPE_NONE:
            mf.after(100, updateMode)
    else:
        mf.after(100, updateMode)  # re-poll the rfid reader in 100 milliseconds

def drinkMode():
    global state
    if user:
        if tkMessageBox.askquestion(title="drink mode", message="Would you like to enter drink mode?") == 'yes':
            state = DRINK_MODE
            mf.setMainText("Now consuming with " + db.getUserName(user))
            mf.after(200, updateDrinkMode)

def updateDrinkMode():
    global user, state
    if state == DRINK_MODE:
        read = rfidReader.waitForTagRead(delay=0.001, timeout=10)
        if read:
            mf.tagRead(read)
            tagType = db.getTagType(read)
            if tagType == RfidReader.TAG_TYPE_DRINK:
                sf.setSidePanelDrink(read, db.getDrinkInfo(read))
                drink = read
                #user = ""
            elif tagType == RfidReader.TAG_TYPE_USER:
                sf.setSidePanelUser(read, db.getUserInfo(read))
                user = read
                mf.setMainText("Now consuming with " + db.getUserName(user))
                drink = ""
            elif tagType == RfidReader.TAG_TYPE_ADMIN:
                pass
            elif tagType == RfidReader.TAG_TYPE_CMPL:
                #todo: consume a drink
                pass

        mf.after(100, updateDrinkMode) #re-poll the rfid reader in 100 milliseconds


def leaveDrinkMode():
    global state, user
    if tkMessageBox.askquestion(title="drink mode", message="Would you like to leave drink mode?") == 'yes':
        mf.after(200, pollReader)
        state = READ_MODE
        sf.clearEntry()
        user = ""
        mf.setMainText("Waiting for Tag Read " )

class mainFrame(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent) #call to superconstructor
        self.parent = parent
        self.config(bg="white")
        self.direction = Label(self, text="Click to connect to RFID device", background="white")
        self.direction.pack()

        self.mainImage = PhotoImage(file="res/Moretti.gif")
        self.offConnImage = PhotoImage(file="res/connect_light_off.gif").subsample(2,2)
        self.onConnImage = PhotoImage(file="res/connect_light_on.gif").subsample(2,2)

        self.connectLight = Label(self, image=self.offConnImage)
        self.connectLight.pack(side = TOP)

        self.mainButton = Label(self, image=self.mainImage)
        self.mainButton.bind("<Button-1>", self.mainClickHandler)
        self.mainButton.pack()

        comports = ""
        for comport in rfidReader.listSerialPorts():
            comports += comport + " "
        self.comList = ttk.Combobox(self, values=comports)
        self.comList.bind("<Button-1>", self.dropClickHandler)
        if comports:
            self.comList.current(0)
        self.comList.pack()
        self.grid(row=0, column=0)

    def mainClickHandler(self, event=None):
        global state
        if not rfidReader.isConnected():
            if self.comList.get():
                resp = tkMessageBox.askquestion(self.parent, message="Connect with Serial port " + self.comList.get())
                if resp == 'yes':
                    connect(self.comList.get())
            else:
                tkMessageBox.showerror(message="Error No Serial Port selected")
        elif state == READ_MODE:
            drinkMode()
        elif state == DRINK_MODE:
            leaveDrinkMode()


    def dropClickHandler(self, event=None):
        if not rfidReader.isConnected():
            comports = ""
            for comport in rfidReader.listSerialPorts():
                comports += comport + " "
            self.comList.config(values=comports)
            if comports:
                self.comList.current(0)

    def setConnected(self):
        self.comList.pack_forget()
        self.direction.config(text="Now waiting for tag read")
        self.connectLight.config(image=self.onConnImage)

    def setLightOn(self):
        self.connectLight.config(image=self.onConnImage)

    def tagRead(self, read):
        self.direction.config(text="last read tag : " + read)
        self.connectLight.config(image=self.offConnImage)
        self.after(300, self.setLightOn)

    def setMainText(self, text):
        self.direction.config(text=text)


class sideFrame(Frame):

    def __init__(self, parent):
        Frame.__init__(self,parent,borderwidth=2, relief = SUNKEN)
        self.config(width=500, height=500)
        self.pack_propagate(0)
        self.label = Label(self)
        self.label.pack(side = TOP)
        self.edit = Button(self, text="edit", state=DISABLED,command=self.updateTag)
        self.edit.pack(side = BOTTOM)
        self.table = SimpleTable(self, rows=4, columns=2)
        self.table.pack(side = BOTTOM)
        self.grid(row= 0, column=1)
        self.tag = ""
        self.text = Text(self, width=44, height=5, state=DISABLED)
        self.textlabel = Label(self, text="Drinks Consumed:")

    def setSidePanelDrink(self, tagId, drinkDbObject):
        self.tag = tagId
        self.table.clear()
        if state == DRINK_MODE:
            self.label.config(text="Current Consuming User is \n" + db.getUserName(user) + " \n consuming "  +drinkDbObject[0]  )
        else:
            self.label.config(text = "Last tag scanned: \n" + drinkDbObject[0])
        self.table.set(0,0, "Name:")
        self.table.set(0, 1, drinkDbObject[0])
        self.table.set(1,0, "Qty:")
        self.table.set(1, 1, str(drinkDbObject[2]) + "ml")
        self.table.set(2,0, "Drug:")
        self.table.set(2, 1, drinkDbObject[1])
        self.table.set(3,0, "Dose:")
        self.table.set(3, 1, str(drinkDbObject[3]) + "mg/ml")
        self.text.pack_forget()
        self.text.delete(1.0, END) #  clears widget
        self.textlabel.pack_forget()

    def setSidePanelUser(self, tagId, userDbObject, isAdmin= False):
        global state
        self.tag = tagId
        self.table.clear()
        if state == DRINK_MODE:
            self.label.config(text="Current Consuming User is \n" + userDbObject[0])
        else:
            self.label.config(text = "Last tag scanned: \n" + userDbObject[0])
        self.table.set(0,0, "Name:")
        self.table.set(0, 1, userDbObject[0])
        self.table.set(1,0, "DOB")
        self.table.set(1, 1, userDbObject[1])
        self.table.set(2,0, "Weight")
        self.table.set(2, 1, str(userDbObject[2]) + " Kg")
        self.table.set(3,0, "----")

        self.table.set(0,0, "Name:")
        self.table.set(0, 1, userDbObject[0])
        self.table.set(1,0, "DOB")
        self.table.set(1, 1, userDbObject[1])
        self.table.set(2,0, "Weight")
        self.table.set(2, 1, str(userDbObject[2]))
        self.table.set(3,0, "----")

        self.text.delete(1.0, END)
        self.text.pack(side = BOTTOM)
        self.text.config(state = NORMAL)

        consumed = db.getDrinksConsumed(tagId)

        for drink in consumed:
            self.text.insert('end', db.getDrinkName(drink[0]) + "\n")

        self.text.config(state = DISABLED)
        self.textlabel.pack(side= BOTTOM)

    def clearEntry(self):
        self.tag = ""
        self.table.clear()
        self.label.config(text = "")
        self.text.delete(1.0, END)

    def enterAdminMode(self):
        self.edit.config(state=ACTIVE)

    def exitAdminMode(self):
        self.edit.config(state = DISABLED)
        self.clearEntry()
        exitUpdateMode()

    def updateTag(self):
        EditWindow(self.tag)
        self.edit.config(state = DISABLED)

class SimpleTable(Frame): #copied from https://stackoverflow.com/questions/11047803/creating-a-table-look-a-like-tkinter to save time
    def __init__(self, parent, rows=10, columns=2):
        # use black background so it "peeks through" to
        # form grid lines
        self.rows = rows
        self.columns = columns
        Frame.__init__(self, parent, background="black")
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = Label(self, borderwidth=0, width=30)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)


        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)


    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

    def get(self, row, column):
        entry = self._widgets[row][column]
        entry.get()

    def clear(self):
        for row in range(self.rows):
            for col in range(self.columns):
                widget = self._widgets[row][col]
                widget.configure(text="")


class EditWindow:

    def __init__(self, tag):
        self.tag = tag
        self.window = Toplevel()
        self.window.title = "Edit Pane"
        self.window.protocol("WM_DELETE_WINDOW", self.exitEditWindow)

        self.frame = Frame(self.window)
        self.mode = RfidReader.TAG_TYPE_NONE


        self.labels = []
        for row in range(4):
            label = Label(self.frame)
            label.grid(row=row, column=0, sticky="nsew", padx=1, pady=1)
            self.labels.append(label)

        self.entries = []
        for row in range(4):
            entry = Entry(self.frame, width=50)
            entry.grid(row=row, column=1, sticky="nsew", padx=1, pady=1)
            self.entries.append(entry)

        self.frame.pack()
        self.save = Button(self.window, text="Save", command=self.saveData)
        self.save.pack()

        tagType = db.getTagType(tag)
        if tagType == RfidReader.TAG_TYPE_DRINK:
            self.populateWithDrink(tag)
        elif tagType == RfidReader.TAG_TYPE_USER:
            self.populateWithUser(tag)


    def exitEditWindow(self):
        sf.exitAdminMode()
        self.window.destroy()

    def populateWithDrink(self, tag):
        self.labels[0].config(text = "Name:")
        self.labels[1].config(text= "Qty:")
        self.labels[2].config(text = "Drug:")
        self.labels[3].config(text = "Dose:")
        self.mode = RfidReader.TAG_TYPE_DRINK

    def populateWithUser(self, tag):
        self.labels[0].config(text = "Name:")
        self.labels[1].config(text= "Dob:")
        self.labels[2].config(text = "Weight")
        self.labels[3].config(text = "---")
        self.mode = RfidReader.TAG_TYPE_USER

    def saveData(self):
        if self.mode == RfidReader.TAG_TYPE_USER:
            pass
        elif self.mode == RfidReader.TAG_TYPE_DRINK:
            pass


if __name__ == '__main__':
    global state, rfidReader, db, mf, user, drink
    #Open serial port & handshake, connect db, open gui window, and begin running gui thread
    rfidReader = RfidReader.RfidReader()
    db = TagDatabase()
    root = Tk()
    root.title("RIFD Beer Coaster")
    root.config(background="white")
    mf = mainFrame(root)
    sf = sideFrame(root)

    root.mainloop()

    user = ""
    drink = ""
    db.disconnect()
    rfidReader.disconnect()