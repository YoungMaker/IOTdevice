from Tkinter import *  #import * for now todo: change import to only the things we need
import tkMessageBox
import ttk as ttk
import RfidReader
from tagdb import TagDatabase

NOT_CONNECTED = -1
READ_MODE = 0
DRINK_MODE =1

class drinkObj():
    #todo: have fields for all of the drink table entries
    pass

class userObj():
    #todo: have fields for all of the user table entries
    pass



def pollReader():
    read = rfidReader.waitForTagRead(delay=0.001, timeout=10)
    if read:
        print read
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
        self.mainImage = PhotoImage(file="res/Moretti.gif")
        self.mainButton = Label(parent, image=self.mainImage)
        self.mainButton.bind("<Button-1>", self.mainClickHandler)
        self.mainButton.pack()
        self.pack()
        comports = ""
        for comport in rfidReader.listSerialPorts():
            comports += comport + " "
        self.comList = ttk.Combobox(parent, values=comports)
        self.comList.current(0)
        self.comList.pack()


    def mainClickHandler(self, event=None):
        if not rfidReader.isConnected():
            resp = tkMessageBox.askquestion(self.parent, message="Connect with COM port " + self.comList.get())
            if resp == 'yes':
                connect(self.comList.get())

    def setConnected(self):
        self.comList.pack_forget()


class sideFrame(Frame):

    def __init__(self, parent):
        pass

if __name__ == '__main__':
    global state, rfidReader, db, mf
    #todo: Open serial port & handshake, open gui window and begin running gui thread
    rfidReader = RfidReader.RfidReader()
    db = TagDatabase()
    root = Tk()
    mf = mainFrame(root)
    root.mainloop()

    db.disconnect()
    rfidReader.disconnect()