from tkinter import *
from tkinter import ttk


class MainMem:

    def __init__(self, cache_tree_view):
        super().__init__()
        self.cache_tree_view = cache_tree_view

    def update_row(self, address, data):     
        item_id = self.cache_tree_view.get_children()[int(address, 2)]
        new_values = (address, data)
        self.cache_tree_view.item(item_id, values=new_values)

    def get_row_values(self, i):
        item_id = self.cache_tree_view.get_children()[int(i, 2)]
        values = self.cache_tree_view.item(item_id)['values']
        return values

    def change_row_color_green(self, block):
        self.cache_tree_view.tag_configure('m'+str(block), background='green2')
        
    def change_row_color_white(self, block):
        self.cache_tree_view.tag_configure('m'+str(block), background='white')
