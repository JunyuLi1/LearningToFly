# p2app/views/empty.py
#
# ICS 33 Spring 2023
# Project 2: Learning to Fly
#
# An empty user interface area, for use when the application first starts up.
#

import tkinter


class EmptyView(tkinter.Frame):
    def __init__(self, parent):
        super().__init__(parent)
