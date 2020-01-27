# package used for reading files
# packages used for dynamic time warping calculations
import math
import os
import sys
# package used for building user interface
import tkinter as tk
from enum import Enum
from tkinter import *

# packages used for plotting figures
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import myplot

import re


class Digit(Enum):
    digit_0 = 0
    digit_1 = 1
    digit_2 = 2
    digit_3 = 3
    digit_4 = 4
    digit_5 = 5
    digit_6 = 6
    digit_7 = 7
    digit_8 = 8
    digit_9 = 9


class FileType(Enum):
    test = 0
    enrollment = 1


# 6 dimensional point
class Point:
    def __init__(self, x, y, x1, y1, x2, y2):
        self.x = x
        self.y = y
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


def min_max_normalization(series):
    min_v = min(series)
    max_v = max(series)
    range_v = max_v - min_v
    return [(element - min_v) / range_v for element in series]


# returns the euclidean distance between point1 and point2
def euclidean_distance(point1: Point, point2: Point):
    return math.sqrt(((point1.x - point2.x) ** 2) +
                     ((point1.y - point2.y) ** 2) +
                     ((point1.x1 - point2.x1) ** 2) +
                     ((point1.y1 - point2.y1) ** 2) +
                     ((point1.x2 - point2.x2) ** 2) +
                     ((point1.y2 - point2.y2) ** 2))


def calculate_time_series(x, y):
    series = []
    normalized_x = min_max_normalization(x)
    normalized_y = min_max_normalization(y)
    # velocity of the first number: x', y'
    x_velocity = []
    y_velocity = []
    # acceleration of the first number: x'', y''
    x_acceleration = []
    y_acceleration = []

    x_velocity.append(0)
    for i in range(1, len(normalized_x)):
        x_velocity.append(normalized_x[i] - normalized_x[i - 1])

    y_velocity.append(0)
    for i in range(1, len(normalized_y)):
        y_velocity.append(normalized_y[i] - normalized_y[i - 1])

    x_acceleration.append(0)
    x_acceleration.append(0)
    for i in range(2, len(x_velocity)):
        x_acceleration.append(x_velocity[i] - x_velocity[i - 1])

    y_acceleration.append(0)
    y_acceleration.append(0)
    for i in range(2, len(y_velocity)):
        y_acceleration.append(y_velocity[i] - y_velocity[i - 1])

    for i in range(len(normalized_x)):
        series.append(Point(normalized_x[i], normalized_y[i], x_velocity[i], y_velocity[i], x_acceleration[i], y_acceleration[i]))
    return series


def read_file(file_path):
    x = []
    y = []
    number_of_events = []
    # open file for read
    file_handler = open(file_path)
    # read file lines
    lines = file_handler.read().splitlines()
    # go through file lines
    for line in lines:
        # if first row
        if len(line.split()) == 1:
            number_of_events.append(int(line.split()[0]))
        else:
            x.append(int(line.split()[0]))
            y.append(int(line.split()[1]))
    # close file
    file_handler.close()
    series = calculate_time_series(x, y)
    return x, y, number_of_events, series


def manual_dtw_calculation(series1, series2):
    n = len(series1)
    m = len(series2)
    dtw_matrix = np.zeros((n, m), dtype=np.float)

    for i in range(0, n):
        for j in range(0, m):
            dtw_matrix[i][j] = sys.float_info.max

    dtw_matrix[0][0] = 0

    for i in range(1, n):
        for j in range(1, m):
            cost = euclidean_distance(series1[i], series2[j])
            dtw_matrix[i][j] = cost + min(dtw_matrix[i - 1][j], dtw_matrix[i][j - 1], dtw_matrix[i - 1][j - 1])

    return dtw_matrix[n - 1][m - 1] / (m + n)


def write_to_file(userid, digit, digit_order, compared_userid, compared_digit, compared_digit_order, distance, label):
    with open("result_file.csv", "a") as file:
        file.write("{},{},{},{},{},{},{},{}\n".format(userid, digit, digit_order, compared_userid, compared_digit,
                                                      compared_digit_order, distance, label))


def write_to_file_4v1(userid, digit, compared_userid, compared_digit, compared_digit_order, distance, label):
    with open("result_file_4v1.csv", "a") as file:
        file.write("{},{},{},{},{},{},{}\n".format(userid, digit, compared_userid, compared_digit,
                                                   compared_digit_order, distance, label))


def create_file():
    file_name = "result_file.csv"
    with open(file_name, "w") as file:
        file.write("userId,digit,digitOrder,comparedUserId,comparedDigit,comparedDigitOrder,score,label\n")
    file_name = "result_file_4v1.csv"
    with open(file_name, "w") as file:
        file.write("userId,digit,comparedUserId,comparedDigit,comparedDigitOrder,score,label\n")


def split_text(text):
    x = [float(s) for s in re.findall(r'-?\d+\.?\d*', text)]
    return int(x[0]), int(x[1]), int(x[2])


def get_enrolment_sample(digit, folder_name, session):
    number_list = os.listdir('e-BioDigit_DB/' + folder_name + '/' + session)
    number_list.sort()
    enrolment_series = []
    user_id = []
    e_digit = []
    digit_order = []
    # Getting the enrolment sample
    for file_name in number_list:
        if digit.name in file_name:
            (id, digit_, order) = split_text(file_name)
            user_id.append(id)
            e_digit.append(digit_)
            digit_order.append(order)
            (x, y, number_of_events, series) = read_file('e-BioDigit_DB/' + folder_name + '/' + session + '/' + file_name)
            enrolment_series.append(series)
    return (user_id[0], e_digit[0], digit_order[0], enrolment_series)


def experimental_protocol(folder_list, session):
    # Creating the files if they are not exist
    create_file()
    for folder_name in folder_list:
        for digit in Digit:
            number_list = os.listdir('e-BioDigit_DB/' + folder_name + '/' + session)
            number_list.sort()
            (user_id, e_digit, digit_order, enrolment_series) = get_enrolment_sample(digit, folder_name, session)
            # Getting the positive samples
            for e_file_name in number_list:
                if digit.name in e_file_name:
                    (x2, y2, number_of_events2, enrolment_series2) = read_file(
                        'e-BioDigit_DB/' + folder_name + '/' + session + '/' + e_file_name)
                    (user_id2, e_digit2, digit_order2) = split_text(e_file_name)
                    distance_4v1 = 0
                    for serie in enrolment_series:
                        distance_4v1 += manual_dtw_calculation(serie, enrolment_series2)
                    distance = manual_dtw_calculation(enrolment_series[0], enrolment_series2)
                    write_to_file(user_id, e_digit, digit_order, user_id2, e_digit2, digit_order2, distance, 1)
                    write_to_file_4v1(user_id, e_digit, user_id2, e_digit2, digit_order2, distance_4v1 / 4, 1)
            # Getting the negative samples
            for folder in (folder for folder in folder_list if folder != folder_name):
                test_files = os.listdir('e-BioDigit_DB/' + folder + '/' + session)
                for test_file_name in test_files:
                    if digit.name in test_file_name:
                        (test_user_id, test_e_digit, test_digit_order) = split_text(test_file_name)
                        if test_digit_order == 10:
                            (x, y, number_of_events, test_series) = read_file(
                                'e-BioDigit_DB/' + folder + '/' + session + '/' + test_file_name)
                            break
                distance2_4v1 = 0
                for serie in enrolment_series:
                    distance2_4v1 += manual_dtw_calculation(serie, test_series)
                distance2 = manual_dtw_calculation(enrolment_series[0], test_series)
                write_to_file_4v1(user_id, e_digit, test_user_id, test_e_digit, test_digit_order, distance2_4v1 / 4, 0)
                write_to_file(user_id, e_digit, digit_order, test_user_id, test_e_digit, test_digit_order, distance2, 0)


class Application(object):
    def __init__(self):
        # arrays used to draw figures (First number)
        self.x = []
        self.y = []
        # multi dimensional time series
        self.series1 = []
        self.series2 = []
        # arrays used to compare two number
        self.compare_x = []
        self.compare_y = []

        self.number_of_events = []
        self.compare_number_of_events = []
        # main window variable
        self.window = tk.Tk()
        # labels and drop down lists frame
        self.mainframe = Frame(self.window)
        # graph variables
        self.figure = plt.Figure(figsize=(4, 2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.graph_x = FigureCanvasTkAgg(self.figure, self.window)
        self.graph_y = FigureCanvasTkAgg(self.figure, self.window)
        self.graph_number = FigureCanvasTkAgg(self.figure, self.window)
        # tkinter variables
        self.folder_name = StringVar(self.mainframe)
        self.session_name = StringVar(self.mainframe)
        self.file_name = StringVar(self.mainframe)
        self.compare_folder_name = StringVar(self.mainframe)
        self.compare_session_name = StringVar(self.mainframe)
        self.compare_file_name = StringVar(self.mainframe)
        # the list of options
        self.folder_list = os.listdir('e-BioDigit_DB/')
        self.folder_list.sort()
        self.compare_folder_list = os.listdir('e-BioDigit_DB/')
        self.compare_folder_list.sort()
        self.session_list = os.listdir('e-BioDigit_DB/' + self.folder_list[0])
        self.session_list.sort()
        self.compare_session_list = os.listdir('e-BioDigit_DB/' + self.compare_folder_list[0])
        self.compare_session_list.sort()
        self.number_list = os.listdir('e-BioDigit_DB/' + self.folder_list[0] + '/' + self.session_list[0])
        self.number_list.sort()
        self.compare_number_list = os.listdir(
            'e-BioDigit_DB/' + self.compare_folder_list[0] + '/' + self.compare_session_list[0])
        self.compare_number_list.sort()
        self.popup_menu = OptionMenu(self.mainframe, self.file_name, *self.number_list)
        self.compare_popup_menu = OptionMenu(self.mainframe, self.compare_file_name, *self.compare_number_list)

        # set the main window title and size
        self.window.title("Number Representation")
        self.window.geometry('690x840')
        # add a grid frame
        self.mainframe.grid(column=0, row=0, sticky=(N, W))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.config(bg='black')
        self.mainframe.pack(side=tk.TOP, anchor=tk.NW)
        # create the drop down lists
        self.create_folder_option_menu()
        self.create_comparison_menu()
        # link functions to drop down value changes
        self.folder_name.trace('w', self.database_folder_changed)
        self.session_name.trace('w', self.session_folder_changed)
        self.file_name.trace('w', self.txt_file_changed)
        self.compare_folder_name.trace('w', self.compare_database_folder_changed)
        self.compare_session_name.trace('w', self.compare_session_folder_changed)
        self.compare_file_name.trace('w', self.compare_txt_file_changed)

        # it generates 2 files with over 89k lines which takes over 10 minutes, comment the below line if you don't want to regenerate it
        experimental_protocol(self.folder_list, self.session_list[1])

        # start the main window
        self.window.mainloop()

    # create the top labels and menus
    def create_folder_option_menu(self):
        # set default option
        self.folder_name.set(self.folder_list[0])
        # Popup Menu1
        Label(self.mainframe, text="Choose a File:", fg='white', bg='black').grid(row=1, column=1)
        popup_menu1 = OptionMenu(self.mainframe, self.folder_name, *self.folder_list)
        popup_menu1.config(background='black', width=6)
        popup_menu1.grid(row=1, column=2)
        # set default option
        self.session_name.set(self.session_list[0])
        # Popup Menu2
        Label(self.mainframe, text="a Session:", fg='white', bg='black').grid(row=1, column=3)
        popup_menu2 = OptionMenu(self.mainframe, self.session_name, *self.session_list)
        popup_menu2.config(background='black', width=10)
        popup_menu2.grid(row=1, column=4)
        # set default option
        self.file_name.set(self.number_list[0])
        # Popup Menu3
        Label(self.mainframe, text="Draw Number:", fg='white', bg='black').grid(row=1, column=5)
        self.popup_menu.config(background='black', width=18)
        self.popup_menu.grid(row=1, column=6)
        self.draw_figures()

    def create_comparison_menu(self):
        # set default option
        self.compare_folder_name.set(self.compare_folder_list[0])
        Label(self.mainframe, text="Choose a File:", fg='white', bg='black').grid(row=2, column=1)
        # Popup Menu1
        popup_menu1 = OptionMenu(self.mainframe, self.compare_folder_name, *self.compare_folder_list)
        popup_menu1.config(background='black', width=6)
        popup_menu1.grid(row=2, column=2)
        # set default option
        self.compare_session_name.set(self.compare_session_list[0])
        # Popup Menu2
        Label(self.mainframe, text="a Session:", fg='white', bg='black').grid(row=2, column=3)
        popup_menu2 = OptionMenu(self.mainframe, self.compare_session_name, *self.compare_session_list)
        popup_menu2.config(background='black', width=10)
        popup_menu2.grid(row=2, column=4)
        # set default option
        self.compare_file_name.set(self.compare_number_list[0])
        # Popup Menu3
        Label(self.mainframe, text="Compare to:", fg='white', bg='black').grid(row=2, column=5)
        self.compare_popup_menu.config(background='black', width=18)
        self.compare_popup_menu.grid(row=2, column=6)

    # on folder popup_menu value change
    def database_folder_changed(self, *args):
        self.folder_name.set(self.folder_name.get())
        self.refresh_file_name_option_menu()

    # on folder popup_menu value change
    def compare_database_folder_changed(self, *args):
        self.compare_folder_name.set(self.compare_folder_name.get())
        self.compare_refresh_file_name_option_menu()

    # on session popup_menu value change
    def session_folder_changed(self, *args):
        self.session_name.set(self.session_name.get())
        self.refresh_file_name_option_menu()

    # on session popup_menu value change
    def compare_session_folder_changed(self, *args):
        self.compare_session_name.set(self.compare_session_name.get())
        self.compare_refresh_file_name_option_menu()

    # on file name popup_menu value change
    def txt_file_changed(self, *args):
        self.file_name.set(self.file_name.get())
        self.draw_figures()

    # on file name popup_menu value change
    def compare_txt_file_changed(self, *args):
        self.compare_file_name.set(self.compare_file_name.get())
        (self.compare_x, self.compare_y, self.compare_number_of_events, self.series2) = read_file(
            "e-BioDigit_DB/" + self.compare_folder_name.get() + "/" + self.compare_session_name.get() + "/" + self.compare_file_name.get())
        manual_dtw_calculation(self.series1, self.series2)

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

    # refresh the option menu, with file name
    def compare_refresh_file_name_option_menu(self):
        # reload file list
        self.compare_number_list = os.listdir(
            'e-BioDigit_DB/' + self.compare_folder_name.get() + '/' + self.compare_session_name.get())
        self.compare_number_list.sort()
        self.compare_file_name.set(self.compare_number_list[0])
        # refresh options
        self.compare_popup_menu["menu"].delete(0, "end")
        for number in self.compare_number_list:
            self.compare_popup_menu["menu"].add_command(label=number,
                                                        command=lambda value=number: self.compare_file_name.set(value))

    def draw_figure_number(self):
        self.figure = plt.Figure(figsize=(3, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.graph_number = FigureCanvasTkAgg(self.figure, self.window)
        self.graph_number.get_tk_widget().pack(side=tk.LEFT, anchor=tk.NW)
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
        (self.x, self.y, self.number_of_events, self.series1) = read_file(
            "e-BioDigit_DB/" + self.folder_name.get() + "/" + self.session_name.get() + "/" + self.file_name.get())
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
        self.x = []
        self.y = []
        self.number_of_events = []


if __name__ == '__main__':
    Application()
    myplot.run()
