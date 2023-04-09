from tkinter import *
from tkinter import ttk
from numpy import random

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
        self.cpu.set_all_blocks_white()

        # Se divide la instruccion en partes
        instruction_parts = instr_string_var.split()
        
        # Se divide la instruccion en partes
        print("\nInstructions parts: ", instruction_parts)
        operation = instruction_parts[1]
        print("Operation: ", operation)

        # Instruccion CALC
        if operation == 'CALC':
            self.bus_string_var.set("CALC")
            print(f"{self.processor_id}: CALC")
            self.bus_queue.put(['P'+str(self.processor_id), 'CALC'])
            return
        
        # Variables necesarias para el procesamiento de read y write
        request_type = None
        address = instruction_parts[2]
        print("Address: ", address)
        new_request_bus = None
        
        # Busca la address de la instr en la cache
        #   Devuelve -1 si no la encuentra
        block_id, block = self.cpu.get_block_in_cache(address)
        
        # Instruccion READ
        if operation == 'READ':
            print("Ejecutando READ:")
            
            # SI encuentra el address de la instr en la cache
            if block != -1:
                
                # Estado del bloque
                state = block[0]
                
                # Si encuentra el bloque pero esta invalido [READ MISS]
                if state == 'I':
                    print("READ MISS - STATE I")
                    request_type = 'READ MISS'
                    self.cpu.change_block_color_red(block_id)
                # Si encuentra el bloque y no esta invalido [READ HIT]
                else:
                    print("READ HIT")
                    request_type = 'READ HIT'
                    # Cambia el bloque encontrado a color verde
                    self.cpu.change_block_color_green(block_id)
            
            # NO encuentra el address de la instr en la cache
            else:    
                print("READ MISS - NOT IN CACHE")
                request_type = 'READ MISS'
                block_id = self.replace_block_set_2way(address)
                print("set_num:", block_id)
            
            # ---- Se actuliza el label de la cache al bus y se agrega un request al bus ----
            self.bus_string_var.set(request_type)
            # new_request_bus = ['Pn','READ MISS', 'bn', address]
            new_request_bus = ['P'+str(self.processor_id), request_type, 'b'+str(block_id), address]
            self.bus_queue.put(new_request_bus)
            print("Request addeed to bus queue: ", new_request_bus)
            return

        # Instruccion WRITE
        elif operation == 'WRITE':
            print("Ejecutando WRITE:")
            data = instruction_parts[4]
            
            # Si el address de la instr esta en la cache
            if block != -1:
                print("WRITE HIT")
                request_type = 'WRITE HIT'
                self.cpu.change_block_color_green(block_id)
                
            # Si el address de la instr no esta en la cache    
            else:       
                print("WRITE MISS")
                request_type = 'WRITE MISS'
                block_id = self.replace_block_set_2way(address) 
            
            # ---- Se actuliza el label de la cache al bus y se agrega un request al bus ----
            self.bus_string_var.set(request_type)
            # new_request_bus = ['Pn','READ MISS', 'bn', address]
            new_request_bus = ['P'+str(self.processor_id), request_type, 'b'+str(block_id), address, data]
            self.bus_queue.put(new_request_bus)
            print("Request addeed to bus queue:", new_request_bus)
            return
        
    # Politica de reemplazo utilizada: I,S,E,M,O
    #   Se reemplaza en ese orden de importancia, I es el que se debe reemplazar
    #   con mas frecuencia y O el que debe evitarse modificar
    def replace_block_set_2way(self, new_block_address):
        print("🧵🧵🧵🧵 replace_block_set_2way 🧵🧵🧵🧵")
        cache_blocks = self.cpu.cache_list # cache_blocks = [['M', 0, 0, '4c4c'], ['I', 0, 0, 0], ['I', 0, 1, 0], ['I', 0, 1, 0]]
        print("cache_blocks:", cache_blocks)
        politica = ['I','S','E','M','O']
        print("politica:", politica)
        
        # La direccion se asocia con el indice 0
        if new_block_address[-1] == '0':
            print("Se debe reemplazar el indice:", 0)
            cache_block_0_set_0_state = cache_blocks[0][0]
            cache_block_1_set_0_state = cache_blocks[1][0]
            print("cache_block_0_set_0_state:", cache_block_0_set_0_state)
            print("cache_block_1_set_0_state:",cache_block_1_set_0_state)
            
            for state in politica:
                if(cache_block_0_set_0_state == state):
                    print("🟠 return: 0")
                    return 0
            
                if(cache_block_1_set_0_state == state):
                    print("🟠 return: 1")
                    return 1
        # La direccion se asocia con el indice 1        
        else:
            print("Se debe reemplazar el indice:", 1)
            cache_block_0_set_1_state = cache_blocks[2][0]
            cache_block_1_set_1_state = cache_blocks[3][0]
            print("cache_block_0_set_1_state:", cache_block_0_set_1_state)
            print("cache_block_1_set_1_state:",cache_block_1_set_1_state)
            for state in politica:
                
                if(cache_block_0_set_1_state == state):
                    print("🟠 return: 2")
                    return 2
            
                if(cache_block_1_set_1_state == state):
                    print("🟠 return: 3")
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
        print("P" + str(self.processor_id) + ": busca el addr:", address)
        for i in range(self.cache_size):
            print("Address block",i,":", self.cache_list[i])
            
            block_addr = str(self.cache_list[i][1]) + str(self.cache_list[i][2])
            block_addr = '0'*(3-len(block_addr))+block_addr
            
            print("block_addr:", block_addr)
            if(block_addr == address):
                print("p" + str(self.processor_id) + ": ✅ SI encontró el addr:", address, " retorna:", i,self.cache_list[i])
                return i,self.cache_list[i]
        print("p" + str(self.processor_id) + ": ❌ NO encontró el addr:", address, " retorna:", -1,-1)
        return -1,-1
    
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
    
    # Cambia el color de un bloque a rojo
    def change_block_color_red(self, block):
        self.cache_tree_view.tag_configure('b'+str(block), background='red')
        
    # Cambia el color de un bloque a blanco
    def change_block_color_white(self, block):
        self.cache_tree_view.tag_configure('b'+str(block), background='white')
        
    def binario_a_decimal(self,num_binario):
        decimal = int(num_binario, 2)
        return decimal
    
