from tkinter import *
from tkinter import ttk
from numpy import random
import time

class CpuController:
    def __init__(self, processor_id, cache_tree_view, instr_string_var, bus_string_var, bus_queue, cpu_freq):
        self.processor_id = processor_id
        self.cache_size = 4
        self.current_instr_string_var = instr_string_var
        self.bus_string_var = bus_string_var
        self.cpu = CpuCore(processor_id, cache_tree_view, self.cache_size)
        self.bus_queue = bus_queue
        self.cpu_freq = cpu_freq
        
    def process_instruction(self, instr_string_var):
        # Se actualiza el StringVar de la instruccion actual
        self.current_instr_string_var.set(instr_string_var) 
        
        # Se mapean los bloques de memoria de los TreeView a un array
        self.cpu.update_cache_list()
        self.cpu.set_all_blocks_white()

        # Se divide la instruccion en partes
        instruction_parts = instr_string_var.split()
        
        if(len(instruction_parts) == 0):
            return
        
        # Se divide la instruccion en partes
        operation = instruction_parts[1]

        # Instruccion CALC
        if operation == 'CALC':
            self.bus_string_var.set("CALC")
            self.bus_queue.put(['P'+str(self.processor_id), 'CALC'])
            return
        
        # Variables necesarias para el procesamiento de read y write
        request_type = None
        address = instruction_parts[2]
        new_request_bus = None
        
        # Busca la address de la instr en la cache
        #   Devuelve -1 si no la encuentra
        block_id, block = self.cpu.get_block_in_cache(address)
        
        # Instruccion READ
        if operation == 'READ':
            # SI encuentra el address de la instr en la cache
            if block != -1:
                
                # Estado del bloque
                state = block[0]
                
                # [READ MISS]: Si encuentra el bloque pero esta invalido 
                if state == 'I':
                    request_type = 'READ MISS'
                    # Cambia el color a salmon
                    self.cpu.change_block_color_read_miss(block_id)
                    
                # [READ HIT]: Si encuentra el bloque y no esta invalido 
                else:
                    request_type = 'READ HIT'
                    # Cambia el bloque encontrado a color SeaGreen1
                    self.cpu.change_block_color_read_hit(block_id)
            
            # NO encuentra el address de la instr en la cache
            else:    
                request_type = 'READ MISS'
                block_id = self.replace_block_set_2way(address)
                # No se pinta nada en el bloque de cache actual
            
            # ---- Se actuliza el label de la cache al bus y se agrega un request al bus ----
            self.bus_string_var.set(request_type)
            new_request_bus = ['P'+str(self.processor_id), request_type, 'b'+str(block_id), address]
            self.bus_queue.put(new_request_bus)
            time.sleep(self.cpu_freq)
            return

        # Instruccion WRITE
        elif operation == 'WRITE':
            data = instruction_parts[4]
            
            # Si el address de la instr esta en la cache local
            if block != -1:
                
                # Estado del bloque
                state = block[0]
                
                # Si encuentra el bloque pero esta en I, O, S [WRITE MISS]
                if state == 'I' or state == 'O' or state == 'S':
                    request_type = 'WRITE MISS'
                    # Cambia el bloque encontrado a color hotpink
                    self.cpu.change_block_color_write_miss(block_id)
                    
                # Si encuentra el bloque y no esta invalido [WRITE HIT]
                else:
                    request_type = 'WRITE HIT'
                    # Cambia el bloque encontrado a color gold
                    self.cpu.change_block_color_write_hit(block_id)
                
            # Si el address de la instr no esta en la cache local
            else:       
                request_type = 'WRITE MISS'
                block_id = self.replace_block_set_2way(address)
                
            # ---- Se actuliza el label de la cache al bus y se agrega un request al bus ----
            self.bus_string_var.set(request_type)
            new_request_bus = ['P'+str(self.processor_id), request_type, 'b'+str(block_id), address, data]
            self.bus_queue.put(new_request_bus)
            time.sleep(self.cpu_freq)
            return
        
    # Politica de reemplazo utilizada: I,S,E,M,O
    #   Se reemplaza en ese orden de importancia, I es el que se debe reemplazar
    #   con mas frecuencia y O el que debe evitarse modificar
    def replace_block_set_2way(self, new_block_address):
        cache_blocks = self.cpu.cache_list # cache_blocks = [['M', 0, 0, '4c4c'], ['I', 0, 0, 0], ['I', 0, 1, 0], ['I', 0, 1, 0]]
        politica = ['I','S','E','M','O']
        
        # La direccion se asocia con el indice 0
        if new_block_address[-1] == '0':
            cache_block_0_set_0_state = cache_blocks[0][0]
            cache_block_1_set_0_state = cache_blocks[1][0]

            for state in politica:
                if(cache_block_0_set_0_state == state):
                    return 0
            
                if(cache_block_1_set_0_state == state):
                    return 1
        # La direccion se asocia con el indice 1        
        else:
            cache_block_0_set_1_state = cache_blocks[2][0]
            cache_block_1_set_1_state = cache_blocks[3][0]
            
            for state in politica:
                
                if(cache_block_0_set_1_state == state):
                    return 2
            
                if(cache_block_1_set_1_state == state):
                    return 3

class CpuCore:

    def __init__(self, processor_id, cache_tree_view, cache_size):
        super().__init__()
        self.processor_id = processor_id
        self.cache_tree_view = cache_tree_view
        self.cache_list = []
        self.cache_size = cache_size
    
    # Actualiza la lista de cache con respecto al treeview
    def update_cache_list(self):
        self.cache_list = []
        for i in range(self.cache_size):
            self.cache_list.append(self.cache_tree_view.item('b'+str(i))['values'])
    
    # Busca una direccion en la cache del procesador y devuelve -1 en caso de no encontrarla
    def get_block_in_cache(self, address):
        block_id, block = -1,-1
        for i in range(self.cache_size):
            
            block_addr = str(self.cache_list[i][1]) + str(self.cache_list[i][2])
            block_addr = '0'*(3-len(block_addr))+block_addr
            
            if(block_addr == address):
                block_id, block = i,self.cache_list[i]
                if(block[0] != 'I'):
                    return block_id, block
                    
        return block_id, block
    
    # Cambia el color de todos los bloques a blanco
    def set_all_blocks_white(self):
        for i in range(self.cache_size):
            self.change_block_color_white(i)

    # Cambia los valores den bloque
    def update_block(self, i, state, addr_mem, index, data):
        new_values = (state, addr_mem, index, data)
        self.cache_tree_view.item('b'+str(i), values=new_values)
        self.update_cache_list()

    # Devuelve los valores de un bloque
    def get_block_values(self, i):
        values = self.cache_tree_view.item('b'+str(i))['values']
        return values

    # Cambia el color de un bloque a verde
    def change_block_color_green(self, block):
        self.cache_tree_view.tag_configure('b'+str(block), background='green2')
        
    # Cambia el color de un bloque a SeaGreen1
    def change_block_color_read_hit(self, block):
        self.cache_tree_view.tag_configure('b'+str(block), background='medium spring green')
        
    # Cambia el color de un bloque a salmon
    def change_block_color_read_miss(self, block):
        self.cache_tree_view.tag_configure('b'+str(block), background='Salmon')
        
    # Cambia el color de un bloque a SeaGreen1
    def change_block_color_write_miss(self, block):
        self.cache_tree_view.tag_configure('b'+str(block), background='tan4')
        
    # Cambia el color de un bloque a gold
    def change_block_color_write_hit(self, block):
        self.cache_tree_view.tag_configure('b'+str(block), background='DarkOrange1')
    
    
    # Cambia el color de un bloque a rojo
    def change_block_color_red(self, block):
        self.cache_tree_view.tag_configure('b'+str(block), background='red')
        
    # Cambia el color de un bloque a blanco
    def change_block_color_white(self, block):
        self.cache_tree_view.tag_configure('b'+str(block), background='white')
        
    def binario_a_decimal(self,num_binario):
        decimal = int(num_binario, 2)
        return decimal
    
