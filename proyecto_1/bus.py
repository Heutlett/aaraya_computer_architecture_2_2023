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
        print("\n\n⬜⬜⬜⬜⬜ Se pinta de blanco toda la memoria principal ⬜⬜⬜⬜⬜")
        for i in range(8):
            self.treeview_main_mem.tag_configure('m'+str(i), background='white')
            
        # Va tomando cabeza de la cola del bus hasta que se vacie
        while not self.request_queue.empty():
            print("\n🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌 Bus process 🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌")
            head_request_queue = self.request_queue.get()   # head_request_queue = ['P0', 'WRITE MISS', 'b0', '101', '2bfe']
            operation = head_request_queue[1].split()[0]    # operation = {READ, WRITE, CALC}
            request_type = head_request_queue[1]                 # bus_msg = {WRITE MISS, WRITE HIT, READ MISS, CALC}
            processor_id = int(head_request_queue[0][1])    # proccesor_id = {0,1,2,3}
            print("head_queue:",head_request_queue)
            print("operation:", operation)
            print("processor_id:", processor_id)
            print("bus_msg:", request_type)
            request_cpu_cache_treeview = self.treeview_cache_list[processor_id]
            
            # Request operation CALC
            if operation == 'CALC':
                print("😈😈😈😈 CALC INSTRUCTION 😈😈😈😈")
                print("⏬ continue")
                continue
            
            cache_block_id = head_request_queue[2]                              # cache_block_id = {b0,b1,b2,b3}
            address_instr = head_request_queue[3]                               # address_instr = {000, 001, 010, 111}
            print("cache_block_id:", cache_block_id)
            cache_block = request_cpu_cache_treeview.item(cache_block_id)['values']    # cache_block = ['I', 0, 0, 0]
            state = cache_block[0]                                              # state: {M,O,E,S,I,M}
            print("cache_block:", cache_block)
            print("address_instr:", address_instr)
            print("state:",state)
            
            # Request operation READ
            if operation == 'READ':
                print("👁️👁️👁️👁️  READ INSTRUCTION  👁️👁️👁️👁️")
                # Request READ MISS
                if request_type == 'READ MISS':
                    print("🔕🔕🔕🔕 READ MISS 🔕🔕🔕🔕")
                    # Si se requiere writeback (state M or O)
                    if state == 'M' or state == 'O':
                        print("📝📝📝📝 WRITE BACK (state = M or O) 📝📝📝📝")
                        # Writeback ---------- cache_block = ['state', tag, index, data] --------------------
                        
                        # Dato a escribir en memoria
                        writeback_data = str(cache_block[3])
                        writeback_data = '0'*(4-len(writeback_data))+writeback_data
                        # Direccion donde se va a escribir en memoria
                        print("writeback_data:", writeback_data)
                        writeback_addr = str(cache_block[1]) + str(cache_block[2])
                        writeback_addr = '0'*(3-len(writeback_addr))+writeback_addr
                        print("writeback_addr:", writeback_addr)
                        mem_block_id = 'm'+str(int(writeback_addr,2))
                        # Se hace el wb actualizando el treeview de la memoria
                        writeback_mem_block = self.treeview_main_mem.item(mem_block_id)['values']
                        print("before writeback_mem_block:",writeback_mem_block)
                        writeback_mem_block[0] = writeback_addr
                        writeback_mem_block[1] = writeback_data
                        print("after writeback_mem_block:",writeback_mem_block)
                        self.treeview_main_mem.item(mem_block_id, values=writeback_mem_block)
                        self.treeview_main_mem.tag_configure(mem_block_id, background='green2')
                        # Hace un sleep de 0.5 segundos para simular el delay de la memoria
                        time.sleep(0.5)
                    
                    # Reemplazo de bloque y lectura de dato
                    print("♻️♻️♻️♻️  Reemplazo de bloque y lectura de dato ♻️♻️♻️♻️")
                    # Busca si hay algun procesador que tenga el bloque que se necesita leer en M or O
                    data_read = self.search_cache_modifiew_owned(address_instr, processor_id)
                    print("data_read:", data_read)
                    print("cache_block:", cache_block)
                    # Se modifica la direccion y el dato del bloque
                    cache_block[1] = address_instr[0:2]
                    cache_block[3] = data_read
                    # Verifica si el address califica para ser E
                    if self.address_is_exclusive(address_instr, processor_id):
                        print("🍕🍕🍕🍕 is Exclusive 🍕🍕🍕🍕")
                        cache_block[0] = 'E'
                    # Verifica si el address califica para ser S
                    else:
                        print("🧀🧀🧀🧀 is shared 🧀🧀🧀🧀")
                        cache_block[0] = 'S'
                    
                    # Actualiza el bloque del treeview
                    request_cpu_cache_treeview.item(cache_block_id, values=cache_block)
                    request_cpu_cache_treeview.tag_configure(cache_block_id, background='green2')
                    # Busca si hay un bloque E con la misma address para cambiarlo a S
                    self.seach_cache_exclusive(address_instr, processor_id)
                    print("cache_block:", cache_block)
                    continue
                else:
                    continue
            # Request operation WRITE
            elif operation == 'WRITE':
                print("✏️✏️✏️✏️  WRITE INSTRUCTION  ✏️✏️✏️✏️")
                data_write = head_request_queue[4]
                print("data_write:", data_write)
                # Request WRITE HIT
                if request_type == 'WRITE HIT':
                    print("✏️✅✏️✅ WRITE HIT ✏️✅✏️✅")
                    print("before cache_block:", cache_block)
                    # Actualiza el bloque con el nuevo dato, direccion y estado M
                    cache_block[0] = 'M'
                    cache_block[1] = address_instr[0:2]
                    cache_block[3] = data_write
                    print("after cache_block:", cache_block)
                    # Actualiza el treeview del bloque y la cambia a color verde
                    request_cpu_cache_treeview.item(cache_block_id, values=cache_block)
                    request_cpu_cache_treeview.tag_configure(cache_block_id, background='green2')
                    # Busca si hay otros bloques con misma address para invalidarlos I
                    self.search_cache_to_invalidate(address_instr, processor_id)
                    continue
                # Request WRITE MISS
                elif request_type == 'WRITE MISS':
                    print("❌✏️❌✏️ WRITE MISS ❌✏️❌✏️")
                    # Si se requiere writeback (state M or O)
                    if state == 'M' or state == 'O':
                        print("📝📝📝📝 WRITE BACK (state = M or O) 📝📝📝📝")
                        # Writeback ------------- cache_block = ['state', tag, index, data] --------------------
                        
                        # Dato a escribir en memoria
                        writeback_data = str(cache_block[3])
                        writeback_data = '0'*(4-len(writeback_data))+writeback_data
                        print("towbdata:", writeback_data)
                        # Direccion donde se va a escribir en memoria
                        writeback_addr = str(cache_block[1]) + str(cache_block[2])
                        writeback_addr = '0'*(3-len(writeback_addr))+writeback_addr
                        print("towaddr:", writeback_addr)
                        mem_block_id = 'm'+str(int(writeback_addr,2))
                        # Se hace el wb actualizando el treeview de la memoria
                        writeback_mem_block = self.treeview_main_mem.item(mem_block_id)['values']
                        print("after writeback_mem_block:", writeback_mem_block)
                        writeback_mem_block[0] = writeback_addr
                        writeback_mem_block[1] = writeback_data
                        print("after writeback_mem_block:", writeback_mem_block)
                        # Actualiza el bloque en memoria y lo cambia color verde
                        self.treeview_main_mem.item(mem_block_id, values=writeback_mem_block)
                        self.treeview_main_mem.tag_configure(mem_block_id, background='green2')
                        # Hace un sleep de 0.5 segundos para simular el delay de la memoria
                        time.sleep(0.5)
                        
                    # Se escribe en cache
                    print("✏️💙✏️💙 WRITE INTO CACHE ✏️💙✏️💙")
                    # Se actualiza el bloque con el nuevo dato, direccion y estado M
                    cache_block[0] = 'M'
                    cache_block[1] = address_instr[0:2]
                    cache_block[3] = data_write
                    print("cache_block:", cache_block)
                    # Se actualiza el treeview del bloque de cache y se cambia a color verde
                    request_cpu_cache_treeview.item(cache_block_id, values=cache_block)
                    request_cpu_cache_treeview.tag_configure(cache_block_id, background='green2')
                    print("item:", cache_block_id)
                    print("tag:", cache_block_id)
                    # Busca si hay otros bloques con misma address para invalidarlos I
                    self.search_cache_to_invalidate(address_instr, processor_id)
                    continue
            else:
                continue
    
    # Busca en todos los bloque en busca de un address para determinar si es E
    #   si lo encuentra y es diferente de I retorna falso, es decir no es E
    #   si no lo encuentra o solo esta en I retorna true
    def address_is_exclusive(self, addr_instr, processor_id):
        print("\n 💙💙💙💙 address_is_exclusive process 💙💙💙💙")
        # Itera sobre todas las caches menos la propia
        for cache_id in range(self.cores):
            cache_treeview = self.treeview_cache_list[cache_id]
            if processor_id != cache_id:
                for i in range(self.cores):
                    block = cache_treeview.item('b'+str(i))['values']
                    block_addr = str(block[1]) + str(block[2])
                    block_addr = '0'*(3-len(block_addr))+block_addr
                    if (block_addr == addr_instr and block[0] != 'I'):
                        print("❌❌❌❌ NO ES UNICO, no será E ❌❌❌❌")
                        print("Se encontró en la cache:", cache_id)
                        return False
        print("✅✅✅✅ ES UNICO, será E ✅✅✅✅")
        return True
    
    # Busca los bloques con el address pasado parametro y los invalida
    def search_cache_to_invalidate(self, addr_instr, processor_id):
        print("\n 💚💚💚💚 search_cache_to_invalidate process 💚💚💚💚")
        # Itera sobre todas las caches menos la propia
        for cache_id in range(self.cores):
            cache_treeview = self.treeview_cache_list[cache_id]
            if processor_id != cache_id:
                for i in range(self.cores):
                    block = cache_treeview.item('b'+str(i))['values']
                    block_addr = str(block[1]) + str(block[2])
                    block_addr = '0'*(3-len(block_addr))+block_addr
                    if block_addr == addr_instr:
                        print("✅✅✅✅ Ha encontrado un bloque que debe invalidar ✅✅✅✅")
                        print("Se encontró en la cache:", cache_id)
                        # cache_block = ['state', tag, index, data]
                        print("✝️ old_block:", block)
                        block = ['I', block_addr[0:2], block_addr[2], '0'*(4-len(str(block[3])))+str(block[3])]
                        print("❇️ new_block:", block)
                        cache_treeview.item('b'+str(i), values=block)
                        # Hace un sleep de 0.5 segundos
                        time.sleep(0.5)
                        # Cambia el color del bloque del treeview a verde
                        cache_treeview.tag_configure('b'+str(i), background='green2')
                        return
        return

    # Busca en las caches si hay bloques en estado M or O de una direccion pasada por parametro
    def search_cache_modifiew_owned(self, addr_instr, processor_id):
        print("\n ❤️❤️❤️❤️ search_modifiew_owned process ❤️❤️❤️❤️")
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
                        print("💟💟💟💟 Ha encontrado un bloque en estado M or O 💟💟💟💟")
                        print("Se encontró en la cache:", cache_id)
                        # cache_block = ['state', tag, index, data]
                        print("✝️ old_block:", block)
                        block = ['O', block_addr[0:2], block_addr[2], '0'*(4-len(str(block[3])))+str(block[3])]
                        print("❇️ new_block:", block)
                        cache_treeview.item('b'+str(i), values=block)
                        # Hace un sleep de 0.5 segundos
                        time.sleep(0.5)
                        # Cambia el color del bloque del treeview a verde
                        cache_treeview.tag_configure('b'+str(i), background='green2')
                        # Retorna el dato del bloque
                        return block[3]

        print("❌❌❌❌ No se ha encontrado un bloque en estado M or O ❌❌❌❌")
        # Se trae el dato de la memoria principal
        mem_block_id = 'm'+str(int(addr_instr,2))
        temp_data_read = str(self.treeview_main_mem.item(mem_block_id)['values'][1])
        # Se cambia el color del bloque en la memoria
        self.treeview_main_mem.tag_configure(mem_block_id, background='green2')
        print("\ntemp_data_read:", temp_data_read)
        return '0'*(4-len(temp_data_read))+temp_data_read
    
    # Busca en las caches si hay un bloque en estado E con la direccion pasada por parametro
    def seach_cache_exclusive(self, addr_instr, processor_id):
        print("\n 💛💛💛💛 seach_exclusive process 💛💛💛💛")
        # Itera sobre todas las caches menos la propia
        for cache_id in range(self.cores):
            cache_treeview = self.treeview_cache_list[cache_id]
            if processor_id != cache_id:
                for i in range(self.cores):
                    block = cache_treeview.item('b'+str(i))['values']
                    block_addr = str(block[1]) + str(block[2])
                    block_addr = '0'*(3-len(block_addr))+block_addr
                    if (block_addr == addr_instr and block[0] == 'E'):
                        print("💌💌💌💌 Encuentra un bloque en estado E 💌💌💌💌")
                        # cache_block = ['state', tag, index, data]
                        print("✝️ old_block:", block)
                        block = ['S', block_addr[0:2], block_addr[2], '0'*(4-len(str(block[3])))+str(block[3])]
                        print("❇️ new_block:", block)
                        cache_treeview.item('b'+str(i), values=block)
                        # Hace un sleep de 0.5 segundos
                        time.sleep(0.5)
                        # Cambia el color del bloque del treeview a verde
                        cache_treeview.tag_configure('b'+str(i), background='green2')
                        return
        return
