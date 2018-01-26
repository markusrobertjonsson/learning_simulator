from LsExceptions import LsGuiException
import LsScript

import tkinter as tk
# from tkinter import *
from tkinter.constants import BOTH, YES
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt

import traceback


class Gui():
    def __init__(self):
        self.simulation_data = None  # A ScriptOutput object

        self.root = tk.Tk()
        self.root.title("Learning Simulator")

        self.scriptLabel = None
        self.scriptField = None
        self.__create_widgets__()

        # self.open_file()  # XXX
        # self.parse()  # XXX

        self.root.mainloop()

    def __create_widgets__(self):
        # The frame containing the widgets
        frame = tk.Frame(self.root)

        # The menu
        menu_root = tk.Menu(self.root)
        menu_file = tk.Menu(menu_root)
        menu_file.add_command(label='Open', command=self.open_file)
        menu_root.add_cascade(label='File', menu=menu_file)
        self.root.config(menu=menu_root)

        # The label
        scriptLabel = tk.Label(
            frame, text='Place your script in the box below or open a text file.')
        scriptLabel.pack(side="top", anchor="w")

        # The Text widget
        self.scriptField = ScrolledText(frame)
        self.scriptField.pack(side="top", fill=BOTH, expand=YES)

        # The Quit button
        # quitButton = tk.Button(frame, text="Quit", command=self.quit)
        # quitButton.pack(side="right")

        # The Close All button
        closefigButton = tk.Button(frame, text="Close All Figures", command=self.close_figs)
        closefigButton.pack(side="right")

        # The Simulate button
        simButton = tk.Button(frame, text="Simulate and Plot", command=self.simulate)
        simButton.pack(side="left")

        # The Plot button
        plotButton = tk.Button(frame, text="Plot", command=self.plot)
        plotButton.pack(side="left")

        frame.pack(fill=BOTH, expand=YES)

    def simulate(self):
        try:
            script = self.scriptField.get("1.0", "end-1c")
            script_obj = LsScript.LsScript(script)
            self.simulation_data = script_obj.run()

            # self.simulation_data.printout()

            script_obj.postproc(self.simulation_data)
        except Exception as ex:
            self.handle_exception(ex)

    def plot(self):
        try:
            if self.simulation_data is None:
                raise LsGuiException("No simulation data to plot.")
            script = self.scriptField.get("1.0", "end-1c")
            script_obj = LsScript.LsScript(script)
            script_obj.postproc(self.simulation_data)
        except Exception as ex:
            self.handle_exception(ex)

    def quit(self):
        self.close_figs()
        self.root.destroy()

    def close_figs(self):
        plt.close("all")

    def handle_exception(self, ex):
        err_msg = ex.args[0]
        # if len(ex.args) == 2:
        #     err_msg = "{0} {1}".format(err_msg, ex.args[1])
        #     # err_msg = err_msg + ex.args[1]
        messagebox.showerror("Error", err_msg)
        print(traceback.format_exc())

    def open_file(self):
        filename = filedialog.askopenfilename()
        # filename = "C:/Python/Python36-32/_Markus/scriptexempel2.txt"  # XXX
        file = open(filename, "r")
        self.scriptField.insert("1.0", file.read())
        file.close()  # Make sure you close the file when done
