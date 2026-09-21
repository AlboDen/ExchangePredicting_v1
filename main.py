# This is a sample Python script.

import matplotlib.pyplot as plt

from shadowProcesses import shadowProcesses
from visual.buttonHandlers import ButtonHandlers
from visual.graph import Graph
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from visual.window import Window
import time

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.



# See PyCharm help at https://www.jetbrains.com/help/pycharm/


if __name__ == '__main__':
    print("start")
    app = Window()
    shadowProcesses.RepeatedServerRequest.run()
    ButtonHandlers()
    app.mainloop()
    print("finish")
