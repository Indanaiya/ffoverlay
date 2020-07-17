import tkinter as tk
import threading
import time
import asyncio
from notifications_provider import NotificationsProvider
from load_configuration import getConfig, updateValue
from overlay_components import *

fg_colour = '#FEFEFE'

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
            self._size = size 
      
        self.gatherable_labels = {}

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
        self._options_labels = []
        self._toggle_panel_button_image = tk.PhotoImage(file=presets['size'][self._size]['mainButton'])
        self._settings_button_image = tk.PhotoImage(file='../res/black_dot_32.png') #TODO Temporary
        self._settings = Settings(self, main=main)
        self._options_panel = tk.Frame(self._root, bg='white')
        self._options_panel.grid(row=0, column=0, sticky='nw')
        self._options_panel_removed = True

        self._toggle_panel_button = tk.Label(self._options_panel, image=self._toggle_panel_button_image, bg='white', borderwidth=0)
        self._toggle_panel_button.grid(row=0, column=0, sticky='nw')
        self._toggle_panel_button.bind('<Button-1>', self.toggleOptionsPanel)
        self._toggle_panel_button.bind('<Enter>', self.hover)
        self._toggle_panel_button.bind('<Leave>', self.unhover)
        self._toggle_panel_button_padding = tk.Label(self._options_panel, height=1, font=('Helvetica', 8), bg='white')
        self._toggle_panel_button_padding.grid(row=1, column=0)

        self._settings_button = tk.Label(self._options_panel, image=self._settings_button_image)
        self._settings_button.bind('<Button-1>', self._settings.showSettings)
        self._options_labels.append(self._settings_button)
        self._settings_button.grid(row=0, column=1, rowspan=2, sticky='w')
        self._settings_button.grid_remove()

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
        if self._options_panel_removed:
            self._options_panel_removed = False
            for i in range(len(self._options_labels)):
                self._options_labels[i].grid(row=0,column=i+1)
        else:
            self._options_panel_removed = True
            for l in self._options_labels:
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
        self.gatherable_labels = {k:v for k,v in args}
        print(self.gatherable_labels)
        self.redrawGatherableLabels()

    def removeAllGatherableLabels(self):
        """Destroys all labels present in the gatherableLabels dictionary then empties the gatherableLabels dictionary"""
        for l in self.gatherable_labels.values():
            l.destroy()
        self.gatherable_labels = {}

    def redrawGatherableLabels(self):
        """Displays all labels in gatherableLabels"""
        i = 2
        for l in self.gatherable_labels.values():
            l.grid(row=i, column=0, columnspan=10, sticky='nw')
            i+=1

    async def removeGatherableLabel(self, key):
        """"Removes the gatherable label named 'key' from the dictionary and destroys it"""
        self.gatherable_labels[key].destroy()
        self.gatherable_labels.pop(key)

    async def addGatherableLabel(self, name, item_info):
        """Creates an InspectableLabel with an associated panel providing additional information (inspectPanel), adds it to the list of displayed gatherable labels, then redraws the list of gatherable labels"""
        INSPECT_PANEL_BG_COLOUR = '#6F7066'#Background colour for the Inspect Panel
        inspect_panel = tk.Frame(self._window, bg=INSPECT_PANEL_BG_COLOUR)
        grid_number = 0 #Iterator for column Number

        if item_info['itemValues']:
            location_label = tk.Label(inspect_panel, fg=fg_colour, bg=INSPECT_PANEL_BG_COLOUR, text=f"Location: {item_info['itemValues']['map']} ({item_info['itemValues']['x']}, {item_info['itemValues']['y']})")
            location_label.grid(row=grid_number, sticky='w')
            grid_number+=1

        if item_info['spawnTime']:
            spawn_time_label = tk.Label(inspect_panel, fg=fg_colour, bg=INSPECT_PANEL_BG_COLOUR, text=f"Spawn Time: {item_info['spawnTime']}:00")#Will need changing if something ever spawns not on the hour
            spawn_time_label.grid(row=grid_number, sticky='w')
            grid_number+=1

        if item_info['despawnTime']:
            despawn_time_label = tk.Label(inspect_panel, fg=fg_colour, bg=INSPECT_PANEL_BG_COLOUR, text=f"Despawn Time: {item_info['despawnTime']}:00")
            despawn_time_label.grid(row=grid_number, sticky='w')
            grid_number+=1

        #TODO priceOnEachServerAndLastUpdateTime
        #TODO buttonToOpenInGamerescape
        label = InspectableLabel(self, self._root, inspect_panel, text=f"{name} | {item_info['price']}gil", font=('Helvetica', presets['size'][self._size]['font-size']), bg='#565356', fg=fg_colour)
        
        self.gatherable_labels[name] = label
        self.redrawGatherableLabels()

class Main():
    """Sets up the App object and provides it with the information it needs to display to the user"""
    def start(self):
        """Starts the application"""
        self.gatherable_labels = {}
        self.config_values = getConfig()
        self.app = App(size=self.config_values['general']['size'], main=self)
        self.notifications_provider_thread = threading.Thread(target = self.setupNotificationsProvider) 
        self.notifications_provider_thread.start()
        self.app.mainloop()

    def restart(self):
        """Checks if the settings have been changed. If they have, the new settings are applied"""
        new_config_values = getConfig()
        if new_config_values == self.config_values:
            return #Don't want to waste time restarting the program if none of the settings changed

        #Don't necessarily need to restart the program if the datacenter changed but the size didn't, but this seems easier to code and it's fast enough
        self.app.destroyWindow()
        self.config_values['general']['size'] = new_config_values['general']['size']
        self.app.setupWindow(size=self.config_values['general']['size'], main=self)

        if new_config_values['general']['datacenter'] != self.config_values['general']['datacenter']:
            self.gatherable_labels = {}
            self.notifications_provider.stopGatherAlerts()
            while not self.notifications_provider_thread.isAlive():
                time.sleep(0.25) #TODO there must be a better way of doing this
            self.config_values['general']['datacenter'] = new_config_values['general']['datacenter']
            self.notifications_provider_thread = threading.Thread(target = self.setupNotificationsProvider)
            self.notifications_provider_thread.start()

        asyncio.run(self.redrawLabels())
        self.app.mainloop()

    def setupNotificationsProvider(self):
        """
        Creates and runs a NotificationsProvider object. \n
        (Should always be run in a seperate thread because it will not stop on its own)
        """
        self.notifications_provider = NotificationsProvider(gatherable_items_location, self.config_values['general']['datacenter'], self.nodeSpawn, self.nodeDespawn)
        self.notifications_provider.beginGatherAlerts()

    async def nodeSpawn(self, name=None, price=None, item_values=None, spawn_time=None, despawn_time=None, market_data=None):
        """Records the information about this node spawn and then tells the app to display a label for it"""
        self.gatherable_labels[name] = {'price':price,'itemValues':item_values,'spawnTime':spawn_time,'despawnTime':despawn_time,'marketData':market_data}
        await self.app.addGatherableLabel(name, self.gatherable_labels[name])

    async def nodeDespawn(self, name=None):
        """Removes the information about this node spawn and tells the app to remove the label for it"""
        self.gatherable_labels.pop(name)
        await self.app.removeGatherableLabel(name)

    async def redrawLabels(self):
        """Tells the app to create labels for all node spawns that this object has information for"""
        for key in self.gatherable_labels.keys():
            await self.app.addGatherableLabel(key, self.gatherable_labels[key])

if __name__ == "__main__":
    main = Main()
    main.start()
