import tkinter as tk
import tkinter.ttk as ttk
import logging


class RcpGui:
    colors=['red','green']
    def __init__(self, save_callback, get_ttw, get_total_month):
        logging.info("RcpGui init")
        self._save = save_callback
        self.get_display = {"": lambda: ("Init", False), "Week": get_ttw, "Month": get_total_month}
        self.root = tk.Tk()
        self.display = None
        self.setup_layout()
        self.root.mainloop()

    def setup_layout(self):
        logging.info("RcpGui setup layout")
        self.root.geometry("375x150")
        frame = tk.Frame(self.root)
        self.display = ttk.Label(frame,background="red", anchor="center")
        self.display.bind("<Button-1>", self.save)
        self.display.pack(fill=tk.BOTH, expand=True)
        #self.display.grid(row=0,column=0, sticky="nsew", padx=1, pady=1)
        side = tk.Frame(self.root)
        self.Mode = tk.StringVar()
        self.Mode.set("Week")
        ttk.Radiobutton(side, variable=self.Mode, text="Week", value="Week").pack()
        ttk.Radiobutton(side, variable=self.Mode, text="Month", value="Month").pack()
        frame.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
        side.pack(expand=True, fill=tk.BOTH)
        self.display_update()

    def display_update(self):
        logging.debug("RcpGui refresh")
        display, working = self.get_display[self.Mode.get()]()
        self.display["text"] = display
        self.display["background"]=self.colors[working]
        self.root.after(1000, self.display_update)

    def save(self, *args):
        logging.info("RcpGui save")
        self._save()
