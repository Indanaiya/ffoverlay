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
    """In charge of displaying information to the user and getting input from the user"""
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
        self._window = tk.Tk()
        self._window.configure(background="white")
        self._window.overrideredirect(True) #Makes the window borderless
        self._window.wm_attributes("-topmost", True) #Window is always on top
        self._window.wm_attributes("-transparentcolor", "white") #Where there was once white there is now transparency

        #Primary display frame
        self._root = tk.Frame(self._window, bg='white')
        self._root.grid(sticky='nw')

        #Options Panel
        self._optionsLabels = []
        self._togglePanelButtonImage = tk.PhotoImage(file=presets['size'][self.size]['mainButton'])
        self._settingsButtonImage = tk.PhotoImage(file='../res/black_dot_32.png') #TODO Temporary
        self._settings = Settings(self, main=main)
        self._optionsPanel = tk.Frame(self._root, bg='white')
        self._optionsPanel.grid(row=0, column=0, sticky='nw')
        self._optionsPanelRemoved = True

        self._togglePanelButton = tk.Label(self._optionsPanel, image=self._togglePanelButtonImage, bg='white', borderwidth=0)
        self._togglePanelButton.grid(row=0, column=0, sticky='nw')
        self._togglePanelButton.bind('<Button-1>', self.toggleOptionsPanel)
        self._togglePanelButton.bind('<Enter>', self.hover)
        self._togglePanelButton.bind('<Leave>', self.unhover)
        self._togglePanelButtonPadding = tk.Label(self._optionsPanel, height=1, font=('Helvetica', 8), bg='white')
        self._togglePanelButtonPadding.grid(row=1, column=0)

        self._settingsButton = tk.Label(self._optionsPanel, image=self._settingsButtonImage)
        self._settingsButton.bind('<Button-1>', self._settings.showSettings)
        self._optionsLabels.append(self._settingsButton)
        self._settingsButton.grid(row=0, column=1, rowspan=2, sticky='w')
        self._settingsButton.grid_remove()

    def mainloop(self):
        self._root.mainloop()

    def destroyWindow(self):
        self._window.destroy()

    def freezeWindow(self):
        self._window.wm_attributes("-disabled", True)

    def unfreezeWindow(self):
        self._window.wm_attributes("-disabled", False)

    def hover(self, event):
        print("Main button moused over")
        #TODO Will change main button image

    def unhover(self, event):
        print("Mouse moved off of main button")
        #TODO Will change main button image

    def toggleOptionsPanel(self, event):
        """Displays the options panel if it is currently hidden, hides it if it is currently visible"""
        if self._optionsPanelRemoved:
            self._optionsPanelRemoved = False
            for i in range(len(self._optionsLabels)):
                self._optionsLabels[i].grid(row=0,column=i+1)
        else:
            self._optionsPanelRemoved = True
            for l in self._optionsLabels:
                l.grid_remove()

    def showInspector(self, label):
        """Displays the label as inspector. Hides the previous inspector if one was already shown"""
        self.hideInspector()
        print("Showing: " + str(label))
        self.inspector = label
        self.inspector.grid(row=0, column=1)

    def hideInspector(self):
        """Hides the currently displayed inspector if one is displayed"""
        try:
            self.inspector.grid_remove()
            self.inspector = None
        except AttributeError as e:#If self.inspector does not exist or has already been destroyed it will be None
            print(f"Unable to destroy inspector: {repr(e)}")
            if self.inspector is not None:
                raise e

    def setGatherableLabels(self, *args:(str, tk.Label)):
        """Empties the gatherableLabels dictionary, adds the provided labels to it, then displays those labels"""
        self.gatherableLabels = {k:v for k,v in args}
        print(self.gatherableLabels)
        self.redrawGatherableLabels()

    def removeAllGatherableLabels(self):
        """Destroys all labels present in the gatherableLabels dictionary then empties the gatherableLabels dictionary"""
        for l in self.gatherableLabels.values():
            l.destroy()
        self.gatherableLabels = {}

    def redrawGatherableLabels(self):
        """Displays all labels in gatherableLabels"""
        i = 2
        for l in self.gatherableLabels.values():
            l.grid(row=i, column=0, columnspan=10, sticky='nw')
            i+=1

    async def removeGatherableLabel(self, key):
        """"Removes the gatherable label named 'key' from the dictionary and destroys it"""
        self.gatherableLabels[key].destroy()
        self.gatherableLabels.pop(key)

    async def addGatherableLabel(self, name, itemInfo):
        """Creates an InspectableLabel with an associated panel providing additional information (inspectPanel), adds it to the list of displayed gatherable labels, then redraws the list of gatherable labels"""
        bgInspectPanel = '#6F7066'#Background colour for the Inspect Panel
        inspectPanel = tk.Frame(self._window, bg=bgInspectPanel)
        gridNumber = 0 #Iterator for column Number

        if itemInfo['itemValues']:
            locationLabel = tk.Label(inspectPanel, fg=fgColor, bg=bgInspectPanel, text=f"Location: {itemInfo['itemValues']['map']} ({itemInfo['itemValues']['x']}, {itemInfo['itemValues']['y']})")
            locationLabel.grid(row=gridNumber, sticky='w')
            gridNumber+=1

        if itemInfo['spawnTime']:
            spawnTimeLabel = tk.Label(inspectPanel, fg=fgColor, bg=bgInspectPanel, text=f"Spawn Time: {itemInfo['spawnTime']}:00")#Will need changing if something ever spawns not on the hour
            spawnTimeLabel.grid(row=gridNumber, sticky='w')
            gridNumber+=1

        if itemInfo['despawnTime']:
            despawnTimeLabel = tk.Label(inspectPanel, fg=fgColor, bg=bgInspectPanel, text=f"Despawn Time: {itemInfo['despawnTime']}:00")
            despawnTimeLabel.grid(row=gridNumber, sticky='w')
            gridNumber+=1

        #TODO priceOnEachServerAndLastUpdateTime
        #TODO buttonToOpenInGamerescape
        label = InspectableLabel(self, self._root, inspectPanel, text=f"{name} | {itemInfo['price']}gil", font=('Helvetica', presets['size'][self.size]['font-size']), bg='#565356', fg=fgColor)
        
        self.gatherableLabels[name] = label
        self.redrawGatherableLabels()

class Main():
    """Sets up the App object and provides it with the information it needs to display to the user"""
    def start(self):
        """Starts the application"""
        self.gatherableLabels = {}
        self.configValues = getConfig()
        self.app = App(size=self.configValues['general']['size'], main=self)
        self.notificationsProviderThread = threading.Thread(target = self.setupNotificationsProvider) 
        self.notificationsProviderThread.start()
        self.app.mainloop()

    def restart(self):
        """Checks if the settings have been changed. If they have, the new settings are applied"""
        newConfigValues = getConfig()
        if newConfigValues == self.configValues:
            return #Don't want to waste time restarting the program if none of the settings changed

        #Don't necessarily need to restart the program if the datacenter changed but the size didn't, but this seems easier to code and it's fast enough
        self.app.destroyWindow()
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
        self.app.mainloop()

    def setupNotificationsProvider(self):
        """
        Creates and runs a NotificationsProvider object. \n
        (Should always be run in a seperate thread because it will not stop on its own)
        """
        self.notificationsProvider = NotificationsProvider(gatheredItemsLocation, f"{universalisUrl}{self.configValues['general']['datacenter']}/", self.nodeSpawn, self.nodeDespawn)
        self.notificationsProvider.beginGatherAlerts()

    async def nodeSpawn(self, name=None, price=None, itemValues=None, spawnTime=None, despawnTime=None, marketData=None):
        """Records the information about this node spawn and then tells the app to display a label for it"""
        self.gatherableLabels[name] = {'price':price,'itemValues':itemValues,'spawnTime':spawnTime,'despawnTime':despawnTime,'marketData':marketData}
        await self.app.addGatherableLabel(name, self.gatherableLabels[name])

    async def nodeDespawn(self, name=None):
        """Removes the information about this node spawn and tells the app to remove the label for it"""
        self.gatherableLabels.pop(name)
        await self.app.removeGatherableLabel(name)

    async def redrawLabels(self):
        """Tells the app to create labels for all node spawns that this object has information for"""
        for key in self.gatherableLabels.keys():
            await self.app.addGatherableLabel(key, self.gatherableLabels[key])

if __name__ == "__main__":
    main = Main()
    main.start()
