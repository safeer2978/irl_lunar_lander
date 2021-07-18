from display import display_loop
import threading

var = 2

class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
        
    def run(self):
        display_loop()
      