from tkinter import *
from tkinter import ttk

class CpuCore:

    def __init__(self, inst_var, bus_msg_var, cache_tree_view):
        super().__init__()
        self.current_instr = inst_var
        self.bus_msg = bus_msg_var
        self.cache_tree_view = cache_tree_view

