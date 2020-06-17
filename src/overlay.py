import tkinter as tk
import threading
import time
import asyncio
from notifications_provider import NotificationsProvider
from load_configuration import *

presets = {'size':{'standard':
                        {'mainButton': '../res/black_dot_16.png',
                        'font-size': 11},
                    'large':
                        {'mainButton': '../res/black_dot_32.png',
                        'font-size': 16}
                    }
            }

#Transparency will only work on windows
class App():
    def __init__(self, size='standard'):
        if not size in presets['size'].keys():
            raise ValueError(f"Did not recognise size: {size}. Expected one of: {presets['size'].keys()}")
        else:
            self.size = size #Need this so value can be accessed outside of class
        #Root:
        self.root = tk.Tk()
        self.root.configure(background="white")
        self.root.overrideredirect(True) #Makes the window borderless
        #self.root.geometry("48x96") #The window dimensions
        self.root.wm_attributes("-topmost", True) #Window is always on top
        #self.root.wm_attributes("-disabled", True) #Draws focus and makes window impossible to interract with
        self.root.wm_attributes("-transparentcolor", "white") #Where there was once white there is now transparency

        #Main button:
        self.image = tk.PhotoImage(file=presets['size'][self.size]['mainButton'])
        self.label = tk.Label(self.root, image=self.image, bg='white', borderwidth=0)
        self.label.bind('<Button-1>', self.click)
        self.label.bind('<Enter>', self.hover)
        self.label.bind('<Leave>', self.unhover)
        self.label.grid(row=0, column=0, sticky='w')
        self.gatherableLabels = {}

    def hover(self, event):
        print("Main button moused over")

    def unhover(self, event):
        print("Mouse moved off of main button")

    def click(self, event):
        print("Main button pressed")

    def setGatherableLabels(self, *args:(str, tk.Label)):
        self.gatherableLabels = {k:v for k,v in args}
        print(self.gatherableLabels)
        self.redrawGatherableLabels()

    async def addGatherableLabel(self, keyLabelPair:(str, tk.Label)):
        key, label = keyLabelPair
        self.gatherableLabels[key] = label
        print(self.gatherableLabels)
        self.redrawGatherableLabels()

    def redrawGatherableLabels(self):
        i = 1
        for l in self.gatherableLabels.values():
            l.grid(row=i, columnspan=2)
            i+=1

    async def removeGatherableLabel(self, key):
        self.gatherableLabels[key].destroy()
        self.gatherableLabels.pop(key)

if __name__ == "__main__":
    async def showSpawnLabel(name=None, price=None):
        await app.addGatherableLabel((name, tk.Label(app.root, text=f"{name} | {price}gil", font=('Helvetica', presets['size'][app.size]['font-size']))))

    async def removeSpawnLabel(name=None):
        await app.removeGatherableLabel(name)

    notificationsProvider = NotificationsProvider('../res/values.json', "https://universalis.app/api/Chaos/", showSpawnLabel, removeSpawnLabel)
    notificationsProviderThread = threading.Thread(target = notificationsProvider.beginGatherAlerts)
    configValues = getConfig()
    app = App(size=configValues['general']['size'])
    notificationsProviderThread.start()
    app.root.mainloop()
