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

class OptionsPanel(tk.Label):
    def __init__(self, root, labels: [], bg='white', height=16):
        super().__init__(root, bg=bg)
        self.labels = labels #I should add checking here maybe
        self.height = height
        for label in self.labels:
            label.config(height=height)

    def hide(self):
        for l in self.labels:
            l.grid_remove()

    def show(self):
        print("Show function called")
        for i in range(len(self.labels)):
            print(f"Displaying: {self.labels[i]}")
            self.labels[i].grid(row=0, column=i)

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
        self.root.wm_attributes("-topmost", True) #Window is always on top
        self.root.wm_attributes("-transparentcolor", "white") #Where there was once white there is now transparency

        #Options Panel
        self.image2 = tk.PhotoImage(file='../res/black_dot_32.png') #Temporary
        self.optionsPanel = OptionsPanel(self.root, [tk.Label(self.root, image=self.image2)], bg="white")
        self.optionsPanel.grid(row=0, column=1, rowspan=2)
        self.optionsPanelRemoved = True

        #Main button:
        self.image = tk.PhotoImage(file=presets['size'][self.size]['mainButton'])
        self.mainLabel = tk.Label(self.root, image=self.image, bg='white', borderwidth=0)
        self.mainLabel.grid(row=0, column=0, sticky='nw')
        self.mainLabel.bind('<Button-1>', self.click)
        self.mainLabel.bind('<Enter>', self.hover)
        self.mainLabel.bind('<Leave>', self.unhover)
        self.optionsLabels = {}
        self.gatherableLabels = {}

    def hover(self, event):
        print("Main button moused over")
        #Will change main button image

    def unhover(self, event):
        print("Mouse moved off of main button")
        #Will change main button image

    def click(self, event):
        if self.optionsPanelRemoved:
            self.optionsPanelRemoved = False
            self.optionsPanel.show()
            print("Panel shown")
        else:
            self.optionsPanelRemoved = True
            self.optionsPanel.hide()
            print("Panel hidden")

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
        i = 2
        for l in self.gatherableLabels.values():
            l.grid(row=i, columnspan=2, sticky='w')
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
