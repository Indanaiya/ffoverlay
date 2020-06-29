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
    def __init__(self, app, inspectPanel, **kwargs):
        super().__init__(app.root, kwargs)
        self.app = app
        self.inspectPanel = inspectPanel
        self.inspectorShown = False
        self.bind('<Button-1>', self.toggleInspector)

    def toggleInspector(self, event):
        if not self.inspectorShown:
            self.app.showInspector(self.inspectPanel)
        else:
            self.app.hideInspector()
        self.inspectorShown = not self.inspectorShown


#Settings window
class Settings():
    def __init__(self, app, main=None):
        self.app=app
        self.main = main
        self.config = getConfig()

    def destroyed(self, event): #Does not save the settings
        self.app.window.wm_attributes("-disabled", False)#Makes the main window interactable again

    def showSettings(self, event):
        print("Settings button pressed.")
        self.app.window.wm_attributes("-disabled", True)#Makes the main window uninteractable
        self.root = tk.Tk()
        self.root.title("Settings")
        self.root.geometry('175x200')
        self.root.bind("<Destroy>", self.destroyed)

        #Size selector:
        self.size = tk.StringVar(self.root) #Stores the string that sizeSelector is. Accessed with self.size.get()
        self.size.set(self.config['general']['size']) #Sets the default for the sizeSelector
        self.sizeLabel = tk.Label(self.root, text="Size: ")
        self.sizeLabel.grid(row=0, column=0)
        self.sizeSelector = tk.OptionMenu(self.root, self.size, *[size for size in presets['size'].keys()])
        self.sizeSelector.grid(row=0, column=1)

        #Datacenter selector:
        self.datacenter = tk.StringVar(self.root)
        self.datacenter.set(self.config['general']['datacenter'])
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
