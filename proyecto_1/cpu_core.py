from tkinter import *
from tkinter import ttk


class CpuController:
    def __init__(self, processor_id, cache_tree_view, instr_string_var, bus_string_var, bus_queue):
        self.processor_id = processor_id
        self.cache_size = 4
        self.current_instr_string_var = instr_string_var
        self.bus_string_var = bus_string_var
        self.cpu = CpuCore(processor_id, cache_tree_view, self.cache_size)
        self.bus_queue = bus_queue
        
    def process_instruction(self, instr_string_var):
        
        print("\tP" + str(self.processor_id) + ": Procesando la instruccion: ", instr_string_var)
        
        # Se actualiza el StringVar de la instruccion actual
        self.current_instr_string_var.set(instr_string_var) 
        
        # Se mapean los bloques de memoria de los TreeView a un array
        self.cpu.update_cache_list()
        self.cpu.set_all_rows_white()

        instruction_parts = instr_string_var.split()
        print("\nInstructions parts: ", instruction_parts)
        operation = instruction_parts[1]
        print("Operation: ", operation)
        
        if operation == 'READ':
            print("Ejecutando read:")
            address = instruction_parts[2]
            print("Address: ", address)
            block_id, block = self.cpu.get_block_in_cache(address)
            
            # Si el address de la instr esta en la cache
            if block != -1:
                
                state = block[0]
                
                if state == 'I':
                    self.bus_string_var.set("READ MISS")
                    print(f"{self.processor_id}: READ MISS - STATE I - {address}")
                    self.bus_queue.put(['P'+str(self.processor_id),'READ_MISS', 'b'+str(block_id), address])
                    print("added to queue: ", 'P'+str(self.processor_id),'READ_MISS', 'b'+str(block_id), address)
                    return
                else:
                    self.bus_string_var.set("READ HIT")
                    self.cpu.change_row_color_green(block_id)
                    self.bus_queue.put(['P'+str(self.processor_id),'READ_HIT', 'b'+str(block_id), address])
                    print("addeed to queue: ", 'P'+str(self.processor_id),'READ_HIT', 'b'+str(block_id), address)
                    print(f"{self.processor_id}: READ HIT {address} ; {block[3]}")
                    return
            
            set_num = 0 # Cambiar por alguna politica
            self.bus_string_var.set("READ MISS")
            print("READ MISS - NOT IN CACHE")
            self.bus_queue.put(['P'+str(self.processor_id),'READ_MISS', 'b'+str(set_num), address])
            print("added to queue: ", 'P'+str(self.processor_id),'READ_MISS', 'b'+str(set_num), address)
            return
            
        elif operation == 'WRITE':
            address = instruction_parts[2]
            data = instruction_parts[4]
            
            block_id, block = self.cpu.get_block_in_cache(address)
            
            # Si el address de la instr esta en la cache
            if block != -1:
                self.bus_string_var.set('WRITE HIT')
                print(f"{self.processor_id}: WRITE HIT {address} ; {block[3]}")
                self.cpu.change_row_color_green(block_id)
                self.bus_queue.put(['P'+str(self.processor_id),'WRITE_HIT', 'b'+str(block_id), address, data])
                print("added to queue:", 'P'+str(self.processor_id),'WRITE_HIT', 'b'+str(block_id), address, data)
                return 
            
            # Si el address de la instr no esta en la cache    
            set_num = 0 # Cambiar por alguna politica
            self.bus_string_var.set("WRITE MISS")
            self.bus_queue.put(['P'+str(self.processor_id),'WRITE_MISS', 'b'+str(set_num), address, data])
            print("WRITE MISS")
            print("added to queue:", 'P'+str(self.processor_id),'WRITE_MISS', 'b'+str(set_num), address, data)
            return
        
        else:
            self.bus_string_var.set("CALC")
            print(f"{self.processor_id}: CALC")
            self.bus_queue.put(['P'+str(self.processor_id), 'CALC'])
            return

class CpuCore:

    def __init__(self, processor_id, cache_tree_view, cache_size):
        super().__init__()
        self.processor_id = processor_id
        self.cache_tree_view = cache_tree_view
        self.cache_list = []
        self.cache_size = cache_size
        
    def update_cache_list(self):
        self.cache_list = []
        for i in range(self.cache_size):
            self.cache_list.append(self.cache_tree_view.item('b'+str(i))['values'])
            
    def get_block_in_cache(self, address):
        print("p" + str(self.processor_id), ": buscando la direccion ", address)
        address = self.binario_a_decimal(address)
        print("addres to decimal: ", address)
        for i in range(self.cache_size):
            print("address block ",i,":", self.cache_list[i])
            if(self.cache_list[i][1] == address):
                print("p" + str(self.processor_id), ": encontró la direccion ", address, " retorna: ", i,self.cache_list[i])
                return i,self.cache_list[i]
        return -1,-1
            
    def set_all_rows_white(self):
        for i in range(self.cache_size):
            self.change_row_color_white(i)

    def update_row(self, i, state, addr_mem, index, data):
        new_values = (state, addr_mem, index, data)
        self.cache_tree_view.item('b'+str(i), values=new_values)
        self.update_cache_list()

    def get_row_values(self, i):
        values = self.cache_tree_view.item('b'+str(i))['values']
        return values

    def change_row_color_green(self, block):
        self.cache_tree_view.tag_configure('b'+str(block), background='green2')
        
    def change_row_color_white(self, block):
        self.cache_tree_view.tag_configure('b'+str(block), background='white')
        
    def binario_a_decimal(self,num_binario):
        decimal = int(num_binario, 2)
        return decimal