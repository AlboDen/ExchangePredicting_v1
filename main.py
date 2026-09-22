from shadowProcesses import shadowProcesses
from visual.buttonHandlers import ButtonHandlers
from visual.window import Window

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
