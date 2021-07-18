import tkinter as tk
from tkinter import *

def display_loop(clickA):
    
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", root.quit)
    
    frame = Frame(root)
    frame.pack()
    
    bottomframe = Frame(root)
    bottomframe.pack( side = BOTTOM )
    
    redbutton = Button(frame, text = 'A', fg ='red', command = clickA)
    redbutton.pack( side = LEFT)
    
    greenbutton = Button(frame, text = 'W', fg='brown', command = clickW)
    greenbutton.pack( side = LEFT )
    
    bluebutton = Button(frame, text ='D', fg ='blue', command = clickD)
    bluebutton.pack( side = LEFT )

    root.mainloop()