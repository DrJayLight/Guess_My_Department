import Tkinter as tk

class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.lb = tk.Listbox(self)
        self.lb.insert("end", "one")
        self.lb.insert("end", "two")
        self.lb.insert("end", "three")
        self.lb.pack(side="top", fill="both", expand=True)

        self.but = tk.Button(self, text = 'set')
        self.but.bind("<Button-1>", self.butclick)
        self.but.pack()

    def butclick(self, event):
        selection=self.lb.curselection()
        value = self.lb.get(selection[0])
        print "selection:", selection, ": '%s'" % value

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()