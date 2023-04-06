from tkinter import *
from tkinter import ttk


class CpuCore:

    def __init__(self, cache_tree_view, inst_var, bus_msg_var):
        super().__init__()
        self.cache_tree_view = cache_tree_view
        self.current_instr = inst_var
        self.bus_msg = bus_msg_var

    def update_row(self, i, state, addr_mem, index, data):
        new_values = (state, addr_mem, index, data)
        self.cache_tree_view.item('b'+str(i), values=new_values)

    def get_row_values(self, i):
        values = self.cache_tree_view.item('b'+str(i))['values']
        return values

    def change_row_color_green(self, block):
        self.cache_tree_view.tag_configure('b'+str(block), background='green2')
        
    def change_row_color_white(self, block):
        self.cache_tree_view.tag_configure('b'+str(block), background='white')
