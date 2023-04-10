import math
import random
from datetime import datetime

def generate_random(a,b):    
    
    seed = datetime.now()
    seed = seed.strftime("%H:%M:%S.%f")

    seed = int(seed.replace(":", "").replace(".", ""))

    # Calculamos un número aleatorio entre a y b a partir del tiempo actual en milisegundos
    numero_aleatorio = (((seed * 1115245 + 12345) // 65536) % (b - a + 1)) + a

    return numero_aleatorio


def poisson(lam, size):
    """
    Genera un arreglo de tamaño `size` de números aleatorios a partir de una distribución de Poisson con tasa `lam`.
    """
    contador = 0
    arreglo_poisson = []
    for _ in range(size):
        k = 0
        p = 1.0
        while p >= math.exp(-lam):
            k = k + 1
            u = random.uniform(0,1)
            p = p * u
            contador = contador + 1
            
        arreglo_poisson.append(k - 1)
    return arreglo_poisson


def generate_instruction(processor_id):
    #operation = random.choice(['READ', 'WRITE', 'CALC'])
    instr_op = ['READ', 'WRITE', 'CALC']
    rand_op_list = poisson(10,3)
    rand_max_op_index = rand_op_list.index(max(rand_op_list))
    operation = instr_op[rand_max_op_index]
    
    address = None
    data = None

    if operation != 'CALC':
        #address = bin(random.randint(0, 7))[2:].zfill(3)
        instr_addr = ['000', '001', '010', '011', '100', '101', '110', '111']
        rand_addr_list = poisson(10,8)
        rand_max_addr_index = rand_addr_list.index(max(rand_addr_list))
        address = instr_addr[rand_max_addr_index]
        
    if operation == 'READ':
        return f"P{processor_id}: {operation} {address}"
    
    if operation == 'WRITE':
        data = hex(random.randint(0, 65535))[2:].zfill(4)
        return f"P{processor_id}: {operation} {address} ; {data}"
    
    return f"P{processor_id}: {operation}"
    

print(generate_instruction(1))