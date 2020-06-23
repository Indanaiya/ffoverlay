import tkinter as tk
import threading
import time
import asyncio
from notifications_provider import NotificationsProvider
from load_configuration import *
from overlay_components import *

fgColor = '#FEFEFE'

#Transparency will only work on windows
class App():
    def __init__(self, size='standard', main=None):
        if not size in presets['size'].keys():
            raise ValueError(f"Did not recognise size: {size}. Expected one of: {presets['size'].keys()}")
        else:
            self.size = size #Need this so value can be accessed outside of class

        self.inspector = None

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

    def showInspector(self, label:tk.Frame):
        self.hideInspector()
        print("Showing: " + str(label))
        self.inspector = label
        self.inspector.grid(row=0, rowspan=4, column=2)

    def hideInspector(self):
        try:
            self.inspector.grid_remove()
            self.inspector = None
        except AttributeError as e:#If self.inspector does not exist or has already been destroyed it will be None
            print("Unable to destroy inspector")
            if self.inspector is not None:
                raise

    def setGatherableLabels(self, *args:(str, tk.Label)):
        self.gatherableLabels = {k:v for k,v in args}
        print(self.gatherableLabels)
        self.redrawGatherableLabels()

    def redrawGatherableLabels(self):
        i = 2
        for l in self.gatherableLabels.values():
            l.grid(row=i, columnspan=2, sticky='nw')
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

    async def showSpawnLabel(self, name=None, price=None, itemValues=None, spawnTime=None, despawnTime=None, marketData=None):
        bgInspectPanel = '#6F7066'
        inspectPanel = tk.Frame(self.app.root, bg=bgInspectPanel)
        gridNumber = 0

        if itemValues:
            locationLabel = tk.Label(inspectPanel, fg=fgColor, bg=bgInspectPanel, text=f"Location: {itemValues['map']} ({itemValues['x']}, {itemValues['y']})")
            locationLabel.grid(row=gridNumber, sticky='w')
            gridNumber+=1

        if spawnTime:
            spawnTimeLabel = tk.Label(inspectPanel, fg=fgColor, bg=bgInspectPanel, text=f"Spawn Time: {spawnTime}:00")#Will need changing if something ever spawns not on the hour
            spawnTimeLabel.grid(row=gridNumber, sticky='w')
            gridNumber+=1

        if despawnTime:
            despawnTimeLabel = tk.Label(inspectPanel, fg=fgColor, bg=bgInspectPanel, text=f"Despawn Time: {despawnTime}:00")
            despawnTimeLabel.grid(row=gridNumber, sticky='w')
            gridNumber+=1

        # priceOnEachServerAndLastUpdateTime
        # buttonToOpenInGamerescape
        label = InspectableLabel(self.app, inspectPanel, text=f"{name} | {price}gil", font=('Helvetica', presets['size'][self.app.size]['font-size']), bg='#565356', fg='#FEFEFE')
        await self.app.addGatherableLabel((name, label))

    async def removeSpawnLabel(self, name=None):
        await self.app.removeGatherableLabel(name)


if __name__ == "__main__":
    main = Main()
    main.start()
