import random

def generate_instruction(processor_id):
    operation = random.choice(['READ', 'WRITE', 'CALC'])
    address = None
    data = None

    if operation != 'CALC':
        address = bin(random.randint(0, 7))[2:].zfill(3)
        
    if operation == 'READ':
        return f"P{processor_id}: {operation} {address}"
    
    if operation == 'WRITE':
        data = hex(random.randint(0, 65535))[2:].zfill(4)
        return f"P{processor_id}: {operation} {address} ; {data}"
    
    return f"P{processor_id}: {operation}"

def set_next_instruction(processor_id, next_inst_string_var):
    next_inst_string_var.set(generate_instruction(processor_id))
    print("\tp"+str(processor_id) + ": Se agrega la instruccion: ", next_inst_string_var.get())