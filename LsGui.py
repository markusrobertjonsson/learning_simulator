from LsExceptions import LsGuiException
import LsScript

import tkinter as tk
from tkinter.constants import BOTH, YES
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt

import traceback
import os

TITLE = "Learning Simulator"
FILETYPES = (('Text files', '*.txt'), ('All files', '*.*'))


class Gui():
    def __init__(self):
        self.file_path = None
        self.simulation_data = None  # A ScriptOutput object

        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.file_quit)

        self.set_title()

        self.scriptLabel = None
        self.scriptField = None
        self._create_widgets()
        self._assign_accelerators()

        self.root.mainloop()

    def _create_widgets(self):
        # The frame containing the widgets
        frame = tk.Frame(self.root)

        # The menu bar
        menu_bar = tk.Menu(self.root, tearoff=0)

        # The File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)  # tearoff = 0: can't be seperated from window
        file_menu.add_command(label="New", underline=0, command=self.file_new)  # , accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", underline=0, command=self.file_open)  # , accelerator="Ctrl+O")
        file_menu.add_command(label="Save", underline=0, command=self.file_save)  # , accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", underline=1, command=self.file_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", underline=1, command=self.file_quit)
        menu_bar.add_cascade(label="File", underline=0, menu=file_menu)

        # The Run menu
        run_menu = tk.Menu(menu_bar, tearoff=0)  # tearoff = 0: can't be seperated from window
        run_menu.add_command(label="Simulate and Plot", underline=0, command=self.simulate, accelerator="F5")
        run_menu.add_command(label="Plot", underline=0, command=self.plot)
        menu_bar.add_cascade(label="Run", underline=0, menu=run_menu)

        # The Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)  # tearoff = 0: can't be seperated from window
        edit_menu.add_command(label="Undo", underline=0, command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", underline=0, command=self.redo, accelerator="Ctrl+Y")
        menu_bar.add_cascade(label="Edit", underline=0, menu=edit_menu)

        self.root.config(menu=menu_bar)

        # The label
        lbltxt = "Place your script in the box below or open a text file"
        # lbltxt = "Simulate: F5, Open: Ctrl+O, Save: Ctrl+S, New: Ctrl+N"
        scriptLabel = tk.Label(frame, text=lbltxt)
        scriptLabel.pack(side="top", anchor="w")

        # The Text widget
        self.scriptField = ScrolledText(frame)
        self.scriptField.pack(side="top", fill=BOTH, expand=YES)

        self.scriptField.config(undo=True)
        self.scriptField.focus_set()

        # self.scriptField.config(
        #     borderwidth=0,
        #     font="{Lucida Sans Typewriter} 12",
        #     foreground="green",
        #     background="black",
        #     insertbackground="white",  # cursor
        #     selectforeground="green",  # selection
        #     selectbackground="#008000",
        #     wrap=tk.WORD,  # use word wrapping
        #     width=64,
        #     undo=True,  # Tk 8.4
        # )

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

    def simulate(self, event=None):
        try:
            script = self.scriptField.get("1.0", "end-1c")
            script_obj = LsScript.LsScript(script)
            self.simulation_data = script_obj.run()
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

    def close_figs(self):
        plt.close("all")

    def handle_exception(self, ex):
        # err_msg = ex.args[0]
        err_msg = str(ex)
        # if len(ex.args) == 2:
        #     err_msg = "{0} {1}".format(err_msg, ex.args[1])
        #     # err_msg = err_msg + ex.args[1]
        messagebox.showerror("Error", err_msg)
        print(traceback.format_exc())

    # def file_open(self):
    #     filename = filedialog.askopenfilename()
    #     # filename = "C:/Python/Python36-32/_Markus/scriptexempel2.txt"  # XXX
    #     file = open(filename, "r")
    #     self.scriptField.delete("1.0", "end-1c")
    #     self.scriptField.insert("1.0", file.read())
    #     self.scriptField.mark_set("insert", "1.0")
    #     file.close()  # Make sure you close the file when done

    def save_changes(self):
        if self.scriptField.edit_modified():
            msg = "This document has been modified. Do you want to save changes?"
            save_changes = messagebox.askyesnocancel("Save?", msg)
            if save_changes is None:  # Cancel
                return False
            elif save_changes is True:  # Yes
                self.file_save()
        return True

    def file_new(self, event=None):
        save_changes = self.save_changes()
        if not save_changes:
            return
        self.scriptField.delete(1.0, "end")
        self.scriptField.edit_modified(False)
        self.scriptField.edit_reset()
        self.file_path = None
        self.set_title()

    def file_open(self, event=None):  # , filepath=None):
        save_changes = self.save_changes()
        if not save_changes:
            return

        # XXX
        initialdir = '.'
        if os.path.isdir('/home/markus/Dropbox/'):
            initialdir = '/home/markus/Dropbox/LearningSimulator/Scripts'

        filepath = filedialog.askopenfilename(filetypes=FILETYPES, initialdir=initialdir)
        if filepath is not None and len(filepath) != 0:
            with open(filepath, encoding="utf-8") as f:
                file_contents = f.read()
            # Set current text to file contents
            self.scriptField.delete(1.0, "end")
            self.scriptField.insert(1.0, file_contents)
            self.scriptField.edit_modified(False)
            self.scriptField.mark_set("insert", "1.0")
            self.file_path = filepath
            self.set_title()

    def file_save(self, event=None):
        self.file_save_as(filepath=self.file_path)

    def file_save_as(self, filepath=None, event=None):
        if filepath is None:
            filepath = filedialog.asksaveasfilename(filetypes=FILETYPES)
            if len(filepath) == 0:  # Empty tuple or empty string is returned if cancelled
                return  # "cancelled"
        try:
            with open(filepath, 'wb') as f:
                text = self.scriptField.get(1.0, "end-1c")
                f.write(bytes(text, 'UTF-8'))
                self.scriptField.edit_modified(False)
                self.file_path = filepath
                self.set_title()
                return  # "saved"
        except IOError as e:
            self.handle_exception(e)
            return  # "cancelled"

    def file_quit(self, event=None):
        save_changes = self.save_changes()
        if not save_changes:
            return
        self.close_figs()
        self.root.destroy()  # sys.exit(0)

    def set_title(self, event=None):
        if self.file_path is not None:
            # title = os.path.basename(self.file_path)
            title = os.path.abspath(self.file_path)
        else:
            title = "Untitled"
        self.root.title(title + " - " + TITLE)

    def undo(self, event=None):
        try:
            self.scriptField.edit_undo()
        except Exception as e:
            self.handle_exception(e)
        return "break"

    def redo(self, event=None):
        self.scriptField.edit_redo()
        return "break"

    def _assign_accelerators(self):
        # self.scriptField.bind("<Control-n>", self.file_new)
        # self.scriptField.bind("<Control-N>", self.file_new)
        # self.scriptField.bind("<Control-o>", self.file_open)
        # self.scriptField.bind("<Control-O>", self.file_open)
        # self.scriptField.bind("<Control-S>", self.file_save)
        # self.scriptField.bind("<Control-s>", self.file_save)
        self.scriptField.bind("<Control-y>", self.redo)
        self.scriptField.bind("<Control-Y>", self.redo)
        self.scriptField.bind("<Control-z>", self.undo)
        self.scriptField.bind("<Control-Z>", self.undo)

        # self.root.bind_class("Text", ",<Control-z>", self.undo)
        # self.root.bind_class("Text", ",<Control-Z>", self.undo)
        # self.root.bind_class("Text", ",<Control-y>", self.redo)
        # self.root.bind_class("Text", ",<Control-Y>", self.redo)

        self.scriptField.bind("<F5>", self.simulate)
