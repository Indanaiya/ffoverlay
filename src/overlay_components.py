import tkinter as tk
from load_configuration import getConfig, updateValue

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

class InspectableLabel(tk.Label):
    def __init__(self, app, root, inspectPanel, **kwargs):
        super().__init__(root, kwargs)
        self.app = app
        self.inspectPanel = inspectPanel
        self.bind('<Button-1>', self.toggleInspector)
    #TODO change colour on hover
    def toggleInspector(self, event):
        if not self.app.inspector or self.app.inspector != self.inspectPanel:
            self.app.showInspector(self.inspectPanel)
        else:
            self.app.hideInspector()

class Settings():
    """Settings window"""
    def __init__(self, app, main=None):
        self._app = app
        self._main = main
        self._config = getConfig()

    def destroyed(self, event):
        """Makes the main window interactable"""
        self._app.unfreezeWindow()

    def showSettings(self, event):
        """Opens the settings window"""
        print("Settings button pressed.")
        self._app.freezeWindow() #Makes the main window uninteractable

        #Window:
        self.root = tk.Tk()
        self.root.title("Settings")
        self.root.geometry('175x200')
        self.root.bind("<Destroy>", self.destroyed)

        #Size selector:
        self.size = tk.StringVar(self.root) #Stores the string that sizeSelector is. Accessed with self.size.get()
        self.size.set(self._config['general']['size']) #Sets the default for the sizeSelector
        sizeLabel = tk.Label(self.root, text="Size: ")
        sizeLabel.grid(row=0, column=0)
        sizeSelector = tk.OptionMenu(self.root, self.size, *[size for size in presets['size'].keys()])
        sizeSelector.grid(row=0, column=1)

        #Datacenter selector:
        self.datacenter = tk.StringVar(self.root)
        self.datacenter.set(self._config['general']['datacenter'])
        datacenterLabel = tk.Label(self.root, text="Datacenter: ")
        datacenterLabel.grid(row=1, column=0)
        datacenterSelector = tk.OptionMenu(self.root, self.datacenter, *[datacenter for datacenter in presets['datacenter'].keys()])
        datacenterSelector.grid(row=1, column=1)

        #Submit button:
        submit = tk.Button(self.root, text="Save Changes", command=self.saveSettings)
        submit.grid(row=2, column=1)
        submit.bind('<Button-1>')

        self.root.mainloop()

    def saveSettings(self):
        """"Saves any changes to the settings, closes the settings window, and reloads the main window"""
        updateValue('size', self.size.get())
        print(f"Updated size to {self.size.get()}")
        updateValue('datacenter', self.datacenter.get())
        print(f"Updated datacenter to {self.datacenter.get()}")
        self.root.destroy()
        if self._main:
            self._main.restart()
