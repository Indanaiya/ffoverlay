import tkinter as tk
import threading
import time
import asyncio
from notifications_provider import NotificationsProvider
from load_configuration import *

presets = {'size':{'standard':
                        {'mainButton': '../res/black_dot_16.png',
                        'font-size': 11,
                        'optionsPanelHeight': 16},
                    'large':
                        {'mainButton': '../res/black_dot_32.png',
                        'font-size': 16,
                        'optionsPanelHeight': 32}
                    },
            'datacenter': { 'Chaos': {'region': 'EU'},
                            'Light': {'region': 'EU'},
                            'Aether': {'region': 'NA'},
                            'Primal': {'region': 'NA'},
                            'Crystal': {'region': 'NA'},
                            'Elemental': {'region': 'JP'},
                            'Gaia': {'region': 'JP'},
                            'Mana': {'region': 'JP'}
                    }
            }

gatheredItemsLocation = '../res/values.json'
universalisUrl = "https://universalis.app/api/"

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
        for i in range(len(self.labels)):
            self.labels[i].grid(row=0, column=i)

#Settings window
class Settings():
    def __init__(self, app, main=None):
        self.app=app
        self.main = main

    def destroyed(self, event): #Does not save the settings
        self.app.root.wm_attributes("-disabled", False)#Makes the main window interactable again

    def showSettings(self, event):
        def printSize():
            print(self.size.get())

        print("Settings button pressed.")
        self.app.root.wm_attributes("-disabled", True)#Makes the main window uninteractable
        self.root = tk.Tk()
        self.root.geometry('250x500')
        self.root.bind("<Destroy>", self.destroyed)

        #Size selector:
        self.size = tk.StringVar(self.root) #Stores the string that sizeSelector is. Accessed with self.size.get()
        self.size.set(self.app.size) #Sets the default for the sizeSelector
        self.sizeLabel = tk.Label(self.root, text="Size: ")
        self.sizeLabel.grid(row=0, column=0)
        self.sizeSelector = tk.OptionMenu(self.root, self.size, *[size for size in presets['size'].keys()])
        self.sizeSelector.grid(row=0, column=1)

        #Datacenter selector:
        self.datacenter = tk.StringVar(self.root)
        self.datacenter.set(getConfig()['general']['datacenter'])
        self.datacenterLabel = tk.Label(self.root, text="Datacenter: ")
        self.datacenterLabel.grid(row=1, column=0)
        self.datacenterSelector = tk.OptionMenu(self.root, self.datacenter, *[datacenter for datacenter in presets['datacenter'].keys()])
        self.datacenterSelector.grid(row=1, column=1)


        #Submit button:
        self.submit = tk.Button(self.root, text="Save Changes", command=self.saveSettings)
        self.submit.grid(row=2, column=1)
        self.submit.bind('<Button-1>')

        self.root.mainloop()

    def saveSettings(self):
        updateValue('size', self.size.get())
        print(f"Updated size to {self.size.get()}")
        updateValue('datacenter', self.datacenter.get())
        print(f"Updated datacenter to {self.datacenter.get()}")
        self.root.destroy()
        if self.main:
            self.main.restart()

#Transparency will only work on windows
class App():
    def __init__(self, size='standard', main=None):
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
        self.settings = Settings(self, main=main)
        self.settingsButton = tk.Label(self.root, image=self.image2)
        self.settingsButton.bind('<Button-1>', self.settings.showSettings)
        self.optionsPanel = OptionsPanel(self.root, [self.settingsButton], bg="white", height=presets['size'][self.size]['optionsPanelHeight'])
        self.optionsPanel.grid(row=0, column=2, rowspan=2)
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
        else:
            self.optionsPanelRemoved = True
            self.optionsPanel.hide()

    def setGatherableLabels(self, *args:(str, tk.Label)):
        self.gatherableLabels = {k:v for k,v in args}
        print(self.gatherableLabels)
        self.redrawGatherableLabels()

    def redrawGatherableLabels(self):
        i = 2
        for l in self.gatherableLabels.values():
            l.grid(row=i, columnspan=2, sticky='w')
            i+=1

    async def addGatherableLabel(self, keyLabelPair:(str, tk.Label)):
        key, label = keyLabelPair
        self.gatherableLabels[key] = label
        print(self.gatherableLabels)
        self.redrawGatherableLabels()

    async def removeGatherableLabel(self, key):
        self.gatherableLabels[key].destroy()
        self.gatherableLabels.pop(key)

class Main():
    def start(self):
        self.configValues = getConfig()
        self.notificationsProvider = NotificationsProvider(gatheredItemsLocation, f"{universalisUrl}{self.configValues['general']['datacenter']}/", self.showSpawnLabel, self.removeSpawnLabel)
        self.notificationsProviderThread = threading.Thread(target = self.notificationsProvider.beginGatherAlerts)
        self.app = App(size=self.configValues['general']['size'], main=self)
        self.notificationsProviderThread.start()
        self.app.root.mainloop()

    def restart(self):
        self.app.root.destroy()
        self.start()

    async def showSpawnLabel(self, name=None, price=None):
        await self.app.addGatherableLabel((name, tk.Label(self.app.root, text=f"{name} | {price}gil", font=('Helvetica', presets['size'][self.app.size]['font-size']))))

    async def removeSpawnLabel(self, name=None):
        await self.app.removeGatherableLabel(name)


if __name__ == "__main__":
    main = Main()
    main.start()
