from Tkinter import *  #import * for now todo: change import to only the things we need
import tkMessageBox
import ttk as ttk
import RfidReader
from tagdb import TagDatabase

NOT_CONNECTED = -1
READ_MODE = 0
DRINK_MODE =1


def pollReader():
    read = rfidReader.waitForTagRead(delay=0.001, timeout=10)
    if read:
        mf.tagRead(read)
        tagType = db.getTagType(read)
        if tagType == RfidReader.TAG_TYPE_DRINK:
            sf.setSidePanelDrink(db.getDrinkInfo(read))
        elif tagType == RfidReader.TAG_TYPE_USER:
            sf.setSidePanelUser(db.getUserInfo(read))

    mf.after(100, pollReader) #re-poll the rfid reader in 100 milliseconds

def connect(COMPORT):
    global rfidReader, state
    rfidReader.connect(COMPORT)
    state = READ_MODE
    mf.setConnected()
    mf.after(200, pollReader) #poll the rfid reader in 200 milliseconds


class mainFrame(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent) #call to superconstructor
        self.parent = parent
        self.config(bg="white")
        self.direction = Label(self, text="Click to connect to RFID device", background="white")
        self.direction.pack()
        self.mainImage = PhotoImage(file="res/Moretti.gif")
        self.mainButton = Label(self, image=self.mainImage)
        self.mainButton.bind("<Button-1>", self.mainClickHandler)
        self.mainButton.pack()
        comports = ""
        for comport in rfidReader.listSerialPorts():
            comports += comport + " "
        self.comList = ttk.Combobox(self, values=comports)
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

    def setConnected(self):
        self.comList.pack_forget()
        self.direction.config(text="Now waiting for tag read")

    def tagRead(self, read):
        self.direction.config(text="last read tag : " + read)

class sideFrame(Frame):

    def __init__(self, parent):
        Frame.__init__(self,parent,borderwidth=2, relief = SUNKEN)
        self.config(width=500, height=500)
        self.pack_propagate(0)
        self.label = Label(self)
        self.label.pack(side = TOP)
        self.table = SimpleTable(self, rows=4, columns=2)
        self.table.pack(side = BOTTOM)
        self.edit = Button(self, text="edit", state=DISABLED)
        self.edit.pack(side = BOTTOM)
        self.grid(row= 0, column=1)

    def setSidePanelDrink(self, drinkDbObject):
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


    def setSidePanelUser(self, userDbObject, isAdmin= False):
        self.table.clear()
        self.label.config(text = userDbObject[0])
        self.table.set(0,0, "Name:")
        self.table.set(0, 1, userDbObject[0])
        self.table.set(1,0, "DOB")
        self.table.set(1, 1, userDbObject[1])
        self.table.set(2,0, "Weight")
        self.table.set(2, 1, str(userDbObject[2]))
        self.table.set(3,0, "----")


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
                label = Label(self, borderwidth=0, width=20)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)


    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

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