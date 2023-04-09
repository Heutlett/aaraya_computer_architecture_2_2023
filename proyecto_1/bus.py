from tkinter import *
import time

class Bus:

    def __init__(self, treeview_main_mem, bus_queue, treeview_cache_list, cores):
        super().__init__()
        self.treeview_main_mem = treeview_main_mem
        self.treeview_cache_list = treeview_cache_list
        self.request_queue = bus_queue
        self.cores = cores

    # Procesa las requests que hay en la cola del bus
    def process_bus_queue(self):
        # Hace un sleep de medio segundo para simular la velocidad de la memoria
        time.sleep(0.5)
        # Resetea el color de los bloques de la mem principal
        for i in range(8):
            self.treeview_main_mem.tag_configure('m'+str(i), background='white')
            
        # Va tomando cabeza de la cola del bus hasta que se vacie
        while not self.request_queue.empty():
            head_request_queue = self.request_queue.get()   # head_request_queue = ['P0', 'WRITE MISS', 'b0', '101', '2bfe']
            operation = head_request_queue[1].split()[0]    # operation = {READ, WRITE, CALC}
            request_type = head_request_queue[1]            # bus_msg = {WRITE MISS, WRITE HIT, READ MISS, CALC}
            processor_id = int(head_request_queue[0][1])    # proccesor_id = {0,1,2,3}
            request_cpu_cache_treeview = self.treeview_cache_list[processor_id]
            
            # Request operation CALC
            if operation == 'CALC':
                continue
            
            cache_block_id = head_request_queue[2]                                      # cache_block_id = {b0,b1,b2,b3}
            address_instr = head_request_queue[3]                                       # address_instr = {000, 001, 010, 111}
            cache_block = request_cpu_cache_treeview.item(cache_block_id)['values']     # cache_block = ['I', 0, 0, 0]
            state = cache_block[0]                                                      # state: {M,O,E,S,I,M}
            
            # Request operation READ
            if operation == 'READ':
                # Request READ MISS
                if request_type == 'READ MISS':
                    # Si se requiere writeback (state M or O)
                    if state == 'M' or state == 'O':
                        # Writeback ---------- cache_block = ['state', tag, index, data] --------------------
                        self.make_write_back(cache_block)
                    
                    # Reemplazo de bloque y lectura de dato
                    # Busca si hay algun procesador que tenga el bloque que se necesita leer en M or O
                    data_read = self.search_cache_modified_owned(address_instr, processor_id)
                    # Se modifica la direccion y el dato del bloque
                    cache_block[1] = address_instr[0:2]
                    cache_block[3] = data_read
                    # Verifica si el address califica para ser E
                    if self.address_is_exclusive(address_instr, processor_id):
                        cache_block[0] = 'E'
                    # Verifica si el address califica para ser S
                    else:
                        cache_block[0] = 'S'
                    
                    # Actualiza el bloque del treeview
                    request_cpu_cache_treeview.item(cache_block_id, values=cache_block)
                    request_cpu_cache_treeview.tag_configure(cache_block_id, background='yellow')
                    time.sleep(0.5)
                    continue
                else:
                    continue
            # Request operation WRITE
            elif operation == 'WRITE':
                data_write = head_request_queue[4]
                # Request WRITE HIT
                if request_type == 'WRITE HIT':
                    # Si hay un WRITE HIT y el bloque esta en M o E no es necesario invalidar otros bloques
                    if(cache_block[0] != 'M' and cache_block[0] != 'E'):
                        # Busca si hay otros bloques con misma address para invalidarlos I
                        self.search_cache_to_invalidate(address_instr, processor_id)
                        
                    # Actualiza el bloque con el nuevo dato, direccion y estado M
                    cache_block[0] = 'M'
                    cache_block[1] = address_instr[0:2]
                    cache_block[3] = data_write
                    # Actualiza el treeview del bloque y la cambia a color Gold
                    request_cpu_cache_treeview.item(cache_block_id, values=cache_block)
                    request_cpu_cache_treeview.tag_configure(cache_block_id, background='Gold')
                    continue
                # Request WRITE MISS
                elif request_type == 'WRITE MISS':
                    # Si se requiere writeback (state M or O)
                    if state == 'M' or state == 'O':
                        # Writeback ------------- cache_block = ['state', tag, index, data] --------------------
                        self.make_write_back(cache_block)
                        
                    # Se escribe en cache
                    # Se actualiza el bloque con el nuevo dato, direccion y estado M
                    cache_block[0] = 'M'
                    cache_block[1] = address_instr[0:2]
                    cache_block[3] = data_write
                    # Se actualiza el treeview del bloque de cache y se cambia a color verde
                    request_cpu_cache_treeview.item(cache_block_id, values=cache_block)
                    request_cpu_cache_treeview.tag_configure(cache_block_id, background='green2')
                    # Busca si hay otros bloques con misma address para invalidarlos I
                    self.search_cache_to_invalidate(address_instr, processor_id)
                    time.sleep(0.5)
                    continue
            else:
                continue
    
    # Realiza WB en memoria
    def make_write_back(self, cache_block):
        
        # Dato a escribir en memoria
        writeback_data = str(cache_block[3])
        writeback_data = '0'*(4-len(writeback_data))+writeback_data
        # Direccion donde se va a escribir en memoria
        writeback_addr = str(cache_block[1]) + str(cache_block[2])
        writeback_addr = '0'*(3-len(writeback_addr))+writeback_addr
        mem_block_id = 'm'+str(int(writeback_addr,2))
        # Se hace el wb actualizando el treeview de la memoria
        writeback_mem_block = self.treeview_main_mem.item(mem_block_id)['values']
        writeback_mem_block[0] = writeback_addr
        writeback_mem_block[1] = writeback_data
        # Actualiza el bloque en memoria y lo cambia color turquoise1
        self.treeview_main_mem.item(mem_block_id, values=writeback_mem_block)
        self.treeview_main_mem.tag_configure(mem_block_id, background='turquoise1')
        # Hace un sleep de 0.5 segundos para simular el delay de la memoria
        time.sleep(0.5)
    
    # Utilizado cuando hay READ MISS:
    # Busca en todas las caches un bloque con el address pasado por parametro 
    #   para determinar si es E si lo encuentra y es diferente de I retorna falso, 
    #   es decir no es E si no lo encuentra o solo esta en I retorna true
    def address_is_exclusive(self, addr_instr, processor_id):
        # Itera sobre todas las caches menos la propia
        for cache_id in range(self.cores):
            cache_treeview = self.treeview_cache_list[cache_id]
            if processor_id != cache_id:
                for i in range(self.cores):
                    block = cache_treeview.item('b'+str(i))['values']
                    block_addr = str(block[1]) + str(block[2])
                    block_addr = '0'*(3-len(block_addr))+block_addr
                    if (block_addr == addr_instr and block[0] != 'I'):
                        return False
        return True
    
    # Busca los bloques con el address pasado parametro y los invalida en caso de que esten ya invalidados
    def search_cache_to_invalidate(self, addr_instr, processor_id):
        # Itera sobre todas las caches menos la propia
        for cache_id in range(self.cores):
            cache_treeview = self.treeview_cache_list[cache_id]
            if processor_id != cache_id:
                for i in range(self.cores):
                    block = cache_treeview.item('b'+str(i))['values']
                    block_addr = str(block[1]) + str(block[2])
                    block_addr = '0'*(3-len(block_addr))+block_addr
                    if block_addr == addr_instr and block[0] != 'I':
                        block = ['I', block_addr[0:2], block_addr[2], '0'*(4-len(str(block[3])))+str(block[3])]
                        cache_treeview.item('b'+str(i), values=block)
                        # Hace un sleep de 0.5 segundos
                        time.sleep(0.5)
                        # Cambia el color del bloque del treeview a salmon
                        cache_treeview.tag_configure('b'+str(i), background='red')
        return

    # Utilizado cuando hay READ MISS:
    # Busca en las caches si hay bloques en estado M or O de una direccion pasada por parametro
    # para obtener el dato sin tener que ir a la memoria
    def search_cache_modified_owned(self, addr_instr, processor_id):
        # Itera sobre todas las caches menos la propia
        for cache_id in range(self.cores):
            cache_treeview = self.treeview_cache_list[cache_id]
            if processor_id != cache_id:
                for i in range(self.cores):
                    block = cache_treeview.item('b'+str(i))['values']
                    block_state = block[0]
                    block_addr = str(block[1]) + str(block[2])
                    block_addr = '0'*(3-len(block_addr))+block_addr
                    if block_addr == addr_instr and (block_state == 'O' or block_state == 'M'):
                        block = ['O', block_addr[0:2], block_addr[2], '0'*(4-len(str(block[3])))+str(block[3])]
                        cache_treeview.item('b'+str(i), values=block)
                        # Hace un sleep de 0.5 segundos
                        time.sleep(0.5)
                        # Cambia el color del bloque del treeview a verde
                        cache_treeview.tag_configure('b'+str(i), background='RoyalBlue1')
                        # Retorna el dato del bloque
                        return block[3]
                    
        # Se trae el dato de la memoria principal
        mem_block_id = 'm'+str(int(addr_instr,2))
        temp_data_read = str(self.treeview_main_mem.item(mem_block_id)['values'][1])
        # Se cambia el color del bloque en la memoria
        self.treeview_main_mem.tag_configure(mem_block_id, background='Magenta2')
        return '0'*(4-len(temp_data_read))+temp_data_read