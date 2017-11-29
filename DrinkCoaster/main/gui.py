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
    read = rfidReader.waitForTagRead(delay=0.001, timeout=10)
    if read:
        mf.tagRead(read)
        tagType = db.getTagType(read)
        if tagType == RfidReader.TAG_TYPE_DRINK:
            sf.setSidePanelDrink(read, db.getDrinkInfo(read))
        elif tagType == RfidReader.TAG_TYPE_USER:
            sf.setSidePanelUser(read, db.getUserInfo(read))
        elif tagType == RfidReader.TAG_TYPE_ADMIN:
            #sf.setSidePanelUser(db.getUserInfo(read), True)
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
    if tkMessageBox.askquestion(title="admin mode", message="Would you like to enter admin mode?"):
        sf.enterAdminMode()
        mf.setMainText("Scan Tag to Update Database")
        state = UPDATE_MODE
        updateMode()

def exitUpdateMode():
    global state
    state = READ_MODE
    sf.exitAdminMode()
    mf.setMainText("Now waiting for tag read")

def updateMode():
    global read
    read = rfidReader.waitForTagRead(delay=0.001, timeout=10)
    if read:
        mf.tagRead(read)
        tagType = db.getTagType(read)
        if tagType == RfidReader.TAG_TYPE_DRINK:
            sf.setSidePanelDrink(read, db.getDrinkInfo(read))
        elif tagType == RfidReader.TAG_TYPE_USER:
            sf.setSidePanelUser(read, db.getUserInfo(read))
        elif tagType == RfidReader.TAG_TYPE_ADMIN:
            #sf.setSidePanelUser(db.getUserInfo(read))
            exitUpdateMode()
    else:
        mf.after(100, updateMode)  # re-poll the rfid reader in 100 milliseconds



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
        if not rfidReader.isConnected():
            if self.comList.get():
                resp = tkMessageBox.askquestion(self.parent, message="Connect with Serial port " + self.comList.get())
                if resp == 'yes':
                    connect(self.comList.get())
            else:
                tkMessageBox.showerror(message="Error No Serial Port selected")

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
        self.editTable = SimpleTable(self, rows=4, columns=2, editable=True)
        self.tag = ""

    def setSidePanelDrink(self, tagId, drinkDbObject):
        self.tag = tagId
        self.table.clear()
        self.label.config(text = drinkDbObject[0])
        self.table.set(0,0, "Name:")
        self.table.set(0, 1, drinkDbObject[0])
        self.table.set(1,0, "Qty:")
        self.table.set(1, 1, str(drinkDbObject[2]) + "ml")
        self.table.set(2,0, "Drug:")
        self.table.set(2, 1, drinkDbObject[1])
        self.table.set(3,0, "Dose:")
        self.table.set(3, 1, str(drinkDbObject[3]) + "mg/ml")

        self.editTable.set(0,0, "Name:")
        self.editTable.set(0, 1, drinkDbObject[0])
        self.editTable.set(1,0, "Qty:")
        self.editTable.set(1, 1, str(drinkDbObject[2]) + "ml")
        self.editTable.set(2,0, "Drug:")
        self.editTable.set(2, 1, drinkDbObject[1])
        self.editTable.set(3,0, "Dose:")
        self.editTable.set(3, 1, str(drinkDbObject[3]) + "mg/ml")


    def setSidePanelUser(self, tagId, userDbObject, isAdmin= False):
        self.tag = tagId
        self.table.clear()
        self.label.config(text = userDbObject[0])
        self.table.set(0,0, "Name:")
        self.table.set(0, 1, userDbObject[0])
        self.table.set(1,0, "DOB")
        self.table.set(1, 1, userDbObject[1])
        self.table.set(2,0, "Weight")
        self.table.set(2, 1, str(userDbObject[2]))
        self.table.set(3,0, "----")

        self.table.set(0,0, "Name:")
        self.table.set(0, 1, userDbObject[0])
        self.table.set(1,0, "DOB")
        self.table.set(1, 1, userDbObject[1])
        self.table.set(2,0, "Weight")
        self.table.set(2, 1, str(userDbObject[2]))
        self.table.set(3,0, "----")

    def enterAdminMode(self):
        self.edit.config(state=ACTIVE)
        self.table.pack_forget()
        self.editTable.pack(side= BOTTOM)

    def exitAdminMode(self):
        self.table.pack(side=BOTTOM)
        self.editTable.pack_forget()

    def updateTag(self):
        if self.tag:
            tagType = db.getTagType(self.tag)
            if tagType == RfidReader.TAG_TYPE_DRINK:
                self.updateTagDrink(self.tag)
            elif tagType == RfidReader.TAG_TYPE_USER:
                self.updateTagUser()

    def updateTagDrink(self, tag):
        print self.editTable.get(0,1)

    def updateTagUser(self):
        pass

class SimpleTable(Frame): #copied from https://stackoverflow.com/questions/11047803/creating-a-table-look-a-like-tkinter to save time
    def __init__(self, parent, rows=10, columns=2, editable=False):
        # use black background so it "peeks through" to
        # form grid lines
        self.rows = rows
        self.columns = columns
        Frame.__init__(self, parent, background="black")
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                if not editable:
                    label = Label(self, borderwidth=0, width=30)
                    label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                    current_row.append(label)
                else:
                    edit = Entry(self, width=30, text="test")
                    edit.grid(row=row, column=column, padx=1, pady=1)
                    current_row.append(edit)
            self._widgets.append(current_row)


        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)


    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

    def get(self, row, column):
        widget = self._widgets[row][column]
        widget.get()

    def clear(self):
        for row in range(self.rows):
            for col in range(self.columns):
                widget = self._widgets[row][col]
                widget.configure(text="")


if __name__ == '__main__':
    global state, rfidReader, db, mf
    #todo: Open serial port & handshake, open gui window and begin running gui thread
    rfidReader = RfidReader.RfidReader()
    db = TagDatabase()
    root = Tk()
    root.title("RIFD Beer Coaster")
    root.config(background="white")
    mf = mainFrame(root)
    sf = sideFrame(root)

    root.mainloop()

    db.disconnect()
    rfidReader.disconnect()