import tkinter as tk

#Transparency will only work on windows

class App():
    def __init__(self):
        #Root:
        self.root = tk.Tk()
        self.root.overrideredirect(True) #Makes the window borderless
        self.root.geometry("48x48") #The window dimensions
        self.root.wm_attributes("-topmost", True) #Window is always on top
        #self.root.wm_attributes("-disabled", True) #Draws focus and makes window impossible to interract with
        self.root.wm_attributes("-transparentcolor", "white") #Where there was once white there is now transparency

        #Main button:
        self.image = tk.PhotoImage(file='black_dot.png')
        self.label = tk.Label(self.root, image=self.image, bg='white')
        self.label.bind('<Button-1>', self.callback_hello)
        self.label.bind('<Enter>', self.callback_hello)
        self.label.bind('<Leave>', self.callback_hello)
        self.label.pack()

    def callback_hello(self, event):
        print("Hello World.")

app = App()
app.root.mainloop()
