import Tkinter as tk #import * for now todo: change import to only the things we need
import RfidReader
from tagdb import TagDatabase

class drinkObj():
    #todo: have fields for all of the drink table entries
    pass

class userObj():
    #todo: have fields for all of the user table entries
    pass

if __name__ == '__main__':
    #todo: Open serial port & handshake, open gui window and begin running gui thread
    comport = raw_input("enter the Serial port number\n")
    reader = RfidReader.RfidReader(comport)
    db = TagDatabase()
    root = tk.Tk()
    w = tk.Label(root, text="Hello World!")
    w.pack()
    root.mainloop()

    db.disconnect()
    reader.disconnect()