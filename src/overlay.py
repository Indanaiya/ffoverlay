import tkinter as tk
import threading
import time
import asyncio
from notifications_provider import NotificationsProvider
from load_configuration import getConfig, updateValue
from overlay_components import *

fgColor = '#FEFEFE'

#Transparency will only work on windows
class App():
    def __init__(self, size='standard', main=None):
        self.inspector = None
        self.setupWindow(size=size, main=main)

    def setupWindow(self, size='standard', main=None):
        if not size in presets['size'].keys():
            raise ValueError(f"Did not recognise size: {size}. Expected one of: {presets['size'].keys()}")
        else:
            self.size = size #Need this so value can be accessed outside of class
      
        self.gatherableLabels = {}

        #Root window:
        self.window = tk.Tk()
        self.window.configure(background="white")
        self.window.overrideredirect(True) #Makes the window borderless
        self.window.wm_attributes("-topmost", True) #Window is always on top
        self.window.wm_attributes("-transparentcolor", "white") #Where there was once white there is now transparency

        #Primary display frame
        self.root = tk.Frame(self.window, bg='white')
        self.root.grid(sticky='nw')

        #Options Panel
        self.optionsLabels = []
        self.togglePanelButtonImage = tk.PhotoImage(file=presets['size'][self.size]['mainButton'])
        self.settingsButtonImage = tk.PhotoImage(file='../res/black_dot_32.png') #Temporary
        self.settings = Settings(self, main=main)
        self.optionsPanel = tk.Frame(self.root, bg='white')
        self.optionsPanel.grid(row=0, column=0, sticky='nw')
        self.optionsPanelRemoved = True

        self.togglePanelButton = tk.Label(self.optionsPanel, image=self.togglePanelButtonImage, bg='white', borderwidth=0)
        self.togglePanelButton.grid(row=0, column=0, sticky='nw')
        self.togglePanelButton.bind('<Button-1>', self.click)
        self.togglePanelButton.bind('<Enter>', self.hover)
        self.togglePanelButton.bind('<Leave>', self.unhover)
        self.togglePanelButtonPadding = tk.Label(self.optionsPanel, height=1, font=('Helvetica', 8), bg='white')
        self.togglePanelButtonPadding.grid(row=1, column=0)

        self.settingsButton = tk.Label(self.optionsPanel, image=self.settingsButtonImage)
        self.settingsButton.bind('<Button-1>', self.settings.showSettings)
        self.optionsLabels.append(self.settingsButton)
        self.settingsButton.grid(row=0, column=1, rowspan=2, sticky='w')
        self.settingsButton.grid_remove()

    def hover(self, event):
        print("Main button moused over")
        #TODO Will change main button image

    def unhover(self, event):
        print("Mouse moved off of main button")
        #TODO Will change main button image

    def click(self, event):
        if self.optionsPanelRemoved:
            self.optionsPanelRemoved = False
            for i in range(len(self.optionsLabels)):
                self.optionsLabels[i].grid(row=0,column=i+1)
        else:
            self.optionsPanelRemoved = True
            for l in self.optionsLabels:
                l.grid_remove()

    def showInspector(self, label):
        self.hideInspector()
        print("Showing: " + str(label))
        self.inspector = label
        self.inspector.grid(row=0, column=1)

    def hideInspector(self):
        try:
            self.inspector.grid_remove()
            self.inspector = None
        except AttributeError as e:#If self.inspector does not exist or has already been destroyed it will be None
            print(f"Unable to destroy inspector: {repr(e)}")
            if self.inspector is not None:
                raise e


    def setGatherableLabels(self, *args:(str, tk.Label)):
        self.gatherableLabels = {k:v for k,v in args}
        print(self.gatherableLabels)
        self.redrawGatherableLabels()

    def removeAllGatherableLabels(self):
        for l in self.gatherableLabels.values():
            l.destroy()
        self.gatherableLabels = {}

    def redrawGatherableLabels(self):
        i = 2
        for l in self.gatherableLabels.values():
            l.grid(row=i, column=0, columnspan=10, sticky='nw')
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
        self.spawnLabels = {}
        self.configValues = getConfig()
        self.app = App(size=self.configValues['general']['size'], main=self)
        self.notificationsProviderThread = threading.Thread(target = self.setupNotificationsProvider) 
        self.notificationsProviderThread.start()
        self.app.root.mainloop()

    def restart(self):
        newConfigValues = getConfig()
        if newConfigValues == self.configValues:
            return #Don't want to waste time restarting the program if none of the settings changed

        #Don't necessarily need to restart the program if the datacenter changed but the size didn't, but this seems easier to code and it's fast enough
        self.app.window.destroy()
        self.configValues['general']['size'] = newConfigValues['general']['size']

        if newConfigValues['general']['datacenter'] != self.configValues['general']['datacenter']:
            self.spawnLabels = {}
            self.notificationsProvider.stopGatherAlerts()
            while not self.notificationsProviderThread.isAlive():
                time.sleep(0.25) #TODO there must be a better way of doing this
            self.configValues['general']['datacenter'] = newConfigValues['general']['datacenter']
            self.notificationsProviderThread = threading.Thread(target = self.setupNotificationsProvider)
            self.notificationsProviderThread.start()

        self.app.setupWindow(size=self.configValues['general']['size'], main=self)
        asyncio.run(self.redrawLabels())
        self.app.root.mainloop()

    def setupNotificationsProvider(self):
        self.notificationsProvider = NotificationsProvider(gatheredItemsLocation, f"{universalisUrl}{self.configValues['general']['datacenter']}/", self.addSpawnLabel, self.removeSpawnLabel)
        while not self.app.root: #Don't try to start the gatherAlerts before the app has bene started
            time.sleep(1)
        self.notificationsProvider.beginGatherAlerts()


    def getApp(self):
        return self.app

    async def addSpawnLabel(self, name=None, price=None, itemValues=None, spawnTime=None, despawnTime=None, marketData=None):
        self.spawnLabels[name] = {'price':price,'itemValues':itemValues,'spawnTime':spawnTime,'despawnTime':despawnTime,'marketData':marketData}
        await self.showSpawnLabel(name)

    async def showSpawnLabel(self, name):
        bgInspectPanel = '#6F7066'#Background colour for the Inspect Panel
        app = self.getApp()#get method so the variable can change each time the this method is called
        itemInfo = self.spawnLabels[name]
        self.inspectPanel = tk.Frame(app.window, bg=bgInspectPanel)#self so it can be used by another method to redraw the spawn labels on restart
        gridNumber = 0 #Iterator for column Number

        if itemInfo['itemValues']:
            locationLabel = tk.Label(self.inspectPanel, fg=fgColor, bg=bgInspectPanel, text=f"Location: {itemInfo['itemValues']['map']} ({itemInfo['itemValues']['x']}, {itemInfo['itemValues']['y']})")
            locationLabel.grid(row=gridNumber, sticky='w')
            gridNumber+=1

        if itemInfo['spawnTime']:
            spawnTimeLabel = tk.Label(self.inspectPanel, fg=fgColor, bg=bgInspectPanel, text=f"Spawn Time: {itemInfo['spawnTime']}:00")#Will need changing if something ever spawns not on the hour
            spawnTimeLabel.grid(row=gridNumber, sticky='w')
            gridNumber+=1

        if itemInfo['despawnTime']:
            despawnTimeLabel = tk.Label(self.inspectPanel, fg=fgColor, bg=bgInspectPanel, text=f"Despawn Time: {itemInfo['despawnTime']}:00")
            despawnTimeLabel.grid(row=gridNumber, sticky='w')
            gridNumber+=1

        #TODO priceOnEachServerAndLastUpdateTime
        #TODO buttonToOpenInGamerescape
        label = InspectableLabel(app, self.inspectPanel, text=f"{name} | {itemInfo['price']}gil", font=('Helvetica', presets['size'][self.app.size]['font-size']), bg='#565356', fg=fgColor)
        await app.addGatherableLabel((name, label))

    async def removeSpawnLabel(self, name=None):
        self.spawnLabels.pop(name)
        await self.getApp().removeGatherableLabel(name)

    async def redrawLabels(self):
        for key in self.spawnLabels.keys():
            await self.showSpawnLabel(key)

if __name__ == "__main__":
    main = Main()
    main.start()
