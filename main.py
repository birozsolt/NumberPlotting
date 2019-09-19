import os
import tkinter as tk
from tkinter import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Application:
    # variables used to draw figures
    x = []
    y = []
    number_of_events = []
    # main window variable
    window = tk.Tk()
    # labels and drop down lists frame
    mainframe = Frame(window)
    # graph variables
    figure = plt.Figure(figsize=(4, 2), dpi=100)
    ax = figure.add_subplot(111)
    graph_x = FigureCanvasTkAgg(figure, window)
    graph_y = FigureCanvasTkAgg(figure, window)
    graph_number = FigureCanvasTkAgg(figure, window)
    # tkinter variables
    folder_name = StringVar(mainframe)
    session_name = StringVar(mainframe)
    file_name = StringVar(mainframe)
    # the list of options
    folder_list = os.listdir('e-BioDigit_DB/')
    folder_list.sort()
    session_list = os.listdir('e-BioDigit_DB/' + folder_list[0])
    session_list.sort()
    number_list = os.listdir('e-BioDigit_DB/' + folder_list[0] + '/' + session_list[0])
    number_list.sort()
    popup_menu = OptionMenu(mainframe, file_name, *number_list)

    def __init__(self):
        # set the main window title and size
        self.window.title("Number Representation")
        self.window.geometry('690x540')
        # add a grid frame
        self.mainframe.grid(column=0, row=0, sticky=(N, W))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.config(bg='black')
        self.mainframe.pack(side=tk.TOP, anchor=tk.NW)
        # create the drop down lists
        self.create_folder_optionmenu()
        # link functions to drop down value changes
        self.folder_name.trace('w', self.database_folder_changed)
        self.session_name.trace('w', self.session_folder_changed)
        self.file_name.trace('w', self.txt_file_changed)
        # start the main window
        self.window.mainloop()

    # create the top labels and menus
    def create_folder_optionmenu(self):
        # set default option
        self.folder_name.set(self.folder_list[0])
        # Popup Menu1
        Label(self.mainframe, text="Choose a File: ", fg='white', bg='black').grid(row=1, column=1)
        popup_menu1 = OptionMenu(self.mainframe, self.folder_name, *self.folder_list)
        popup_menu1.config(background='black', width=5)
        popup_menu1.grid(row=1, column=2)
        # set default option
        self.session_name.set(self.session_list[0])
        # Popup Menu2
        Label(self.mainframe, text=" Choose a Session: ", fg='white', bg='black').grid(row=1, column=3)
        popup_menu2 = OptionMenu(self.mainframe, self.session_name, *self.session_list)
        popup_menu2.config(background='black', width=9)
        popup_menu2.grid(row=1, column=4)
        # set default option
        self.file_name.set(self.number_list[0])
        # Popup Menu3
        Label(self.mainframe, text=" Choose a Number: ", fg='white', bg='black').grid(row=1, column=5)
        self.popup_menu.config(background='black', width=17)
        self.popup_menu.grid(row=1, column=6)
        self.draw_figures()

    # on folder popup_menu value change
    def database_folder_changed(self, *args):
        self.folder_name.set(self.folder_name.get())
        self.refresh_file_name_option_menu()

    # on session popup_menu value change
    def session_folder_changed(self, *args):
        self.session_name.set(self.session_name.get())
        self.refresh_file_name_option_menu()

    # on file name popup_menu value change
    def txt_file_changed(self, *args):
        self.file_name.set(self.file_name.get())
        self.draw_figures()

    # refresh the option menu, with file name
    def refresh_file_name_option_menu(self):
        # reload file list
        self.number_list = os.listdir('e-BioDigit_DB/' + self.folder_name.get() + '/' + self.session_name.get())
        self.number_list.sort()
        self.file_name.set(self.number_list[0])
        # refresh options
        self.popup_menu["menu"].delete(0, "end")
        for number in self.number_list:
            self.popup_menu["menu"].add_command(label=number, command=lambda value=number: self.file_name.set(value))

    def draw_figure_number(self):
        self.figure = plt.Figure(figsize=(3, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.graph_number = FigureCanvasTkAgg(self.figure, self.window)
        self.graph_number.get_tk_widget().pack(side=tk.LEFT, anchor=tk.NW, fill=tk.Y)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_xlim([0, 250])
        self.ax.set_ylim([0, 300])
        self.ax.invert_yaxis()
        self.ax.plot(self.x, self.y)
        self.ax.set_title('Represented Number')

    def draw_figure_x(self):
        self.figure = plt.Figure(figsize=(4, 2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.graph_x = FigureCanvasTkAgg(self.figure, self.window)
        self.graph_x.get_tk_widget().pack(side=tk.TOP, anchor=tk.E)
        self.ax.plot(list(range(1, self.number_of_events[0] + 1)), self.x)
        self.ax.set_title('X Coord Linear')

    def draw_figure_y(self):
        self.figure = plt.Figure(figsize=(4, 2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.graph_y = FigureCanvasTkAgg(self.figure, self.window)
        self.graph_y.get_tk_widget().pack(side=tk.TOP, anchor=tk.E)
        self.ax.plot(list(range(1, self.number_of_events[0] + 1)), self.y)
        self.ax.set_title('Y Coord Linear')

    def draw_figures(self):
        # open file for read
        file_handler = open(
            "e-BioDigit_DB/" + self.folder_name.get() + "/" + self.session_name.get() + "/" + self.file_name.get())
        # read file lines
        lines = file_handler.read().splitlines()
        # go through file lines
        for line in lines:
            # if first row
            if len(line.split()) == 1:
                self.number_of_events.append(int(line.split()[0]))
            else:
                self.x.append(int(line.split()[0]))
                self.y.append(int(line.split()[1]))
        # close file
        file_handler.close()
        # remove graphs and redraw
        self.graph_number.get_tk_widget().pack_forget()
        self.graph_number.get_tk_widget().destroy()
        self.draw_figure_number()
        self.graph_x.get_tk_widget().pack_forget()
        self.graph_x.get_tk_widget().destroy()
        self.draw_figure_x()
        self.graph_y.get_tk_widget().pack_forget()
        self.graph_y.get_tk_widget().destroy()
        self.draw_figure_y()

        self.x.clear()
        self.y.clear()
        self.number_of_events.clear()


if __name__ == '__main__':
    Application()
