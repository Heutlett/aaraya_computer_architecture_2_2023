from tkinter import *
from tkinter import ttk
from cpu_core import CpuCore
from PIL import Image, ImageTk

class MainWindow():
    def __init__(self, root):
        super().__init__()

        # Tkinter frames
        root_frame = ttk.Frame(root)
        buttons_frame = ttk.Frame(root_frame, padding= "30 30 30 30")
        tables_frame = ttk.Frame(root_frame, padding= "30 0 0 0")

        self.cores = 4
        self.cpu_list = []
        self.table_list = []

        self.cpu_table_headers = ('state', 'addr', 'index', 'data')
        self.cpu_table_headers_text = ('State', 'Addr mem', 'Index', 'Data')

        self.current_instr_list = []
        self.next_instr_list = []
        self.bus_msgs_list = []

        # Buttons
        self.button_start = ttk.Button(
            buttons_frame, text='Start', command=self.start)

        self.button_next = ttk.Button(
            buttons_frame, text='Next', command=self.next)

        self.button_stop = ttk.Button(
            buttons_frame, text='Stop', command=self.stop)
        
        # Cpu cores widgets
        cpu_title_labels = []

        # Initialize Cpu core lists and TreeViews
        for i in range(self.cores):
            # Variables
            self.current_instr_list.append(StringVar())
            self.next_instr_list.append(StringVar())
            self.bus_msgs_list.append(StringVar())
            # Widgets
            cpu_title_labels.append(ttk.Label(tables_frame, text='N'+str(i), font = "Arial 16 bold"))
            self.table_list.append(ttk.Treeview(
                tables_frame, columns=self.cpu_table_headers, height=4))
            
        self.main_mem_table = ttk.Treeview(tables_frame, columns=('address', 'data'), show='headings', height=16)

        self.table_list.append(self.main_mem_table)

        # Creating Cpu cores
        for i in range(self.cores):
            self.cpu_list.append(CpuCore(
                self.table_list[i], self.current_instr_list[i], self.bus_msgs_list[i]))
            # First column block
            self.table_list[i].column('#0', width=60)
            self.table_list[i].heading('#0', text='Block')

            for e in range(self.cores):
                # Columns ['0=State', '1=Dir', '2=Index', '3=Data']
                self.table_list[i].column(
                    self.cpu_table_headers[e], width=65, anchor='center')
                self.table_list[i].heading(
                    self.cpu_table_headers[e], text=self.cpu_table_headers_text[e])

        # Initialize Cpu cores data with default values
        for i in range(self.cores):
            self.table_list[i].insert(
                '', 'end', 'b0', text='B0', values=('I', '000', '0', '0000'))
            self.table_list[i].insert(
                '', 'end', 'b1', text='B1', values=('I', '000', '0', '0000'))
            self.table_list[i].insert(
                '', 'end', 'b2', text='B2', values=('I', '000', '1', '0000'))
            self.table_list[i].insert(
                '', 'end', 'b3', text='B3', values=('I', '000', '1', '0000'))
            
        self.main_mem_table.column('address', width=70, anchor='center')
        self.main_mem_table.heading('address', text='Address')
        self.main_mem_table.column('data', width=70, anchor='center')
        self.main_mem_table.heading('data', text='Data')

        for i in range(16):
            self.main_mem_table.insert('', 'end', 'm'+str(i), text='M'+str(i), values=('I', '0000'))

        # Positioning frames
        root_frame.grid(column=0, row=0)
        buttons_frame.grid(column=0, row=0)
        tables_frame.grid(column=0, row=1)

        self.button_start.grid(column=0, row=0)
        self.button_next.grid(column=1, row=0)
        self.button_stop.grid(column=2, row=0)

        # Positioning Cpu cores tables
        for i in range(self.cores):
            cpu_title_labels[i].grid(column=i, row=0)
            self.table_list[i].grid(
                column=i, row=1, padx=15, pady=5, columnspan=1)
            
        # Creating and positioning bus image
        bus_img = Image.open("bus_img.png")
        bus_img_tk = ImageTk.PhotoImage(bus_img)
        bus_img_label = ttk.Label(tables_frame, image=bus_img_tk)
        bus_img_label.image = bus_img_tk
        bus_img_label.grid(column=0, row=2, columnspan=4, pady=10)
        
        # Positioning main memory tables
        self.main_mem_table.grid(column=0, row=3, columnspan=4, sticky=(N))


    def start():
        pass

    def next():
        pass

    def stop():
        pass


if __name__ == "__main__":
    root = Tk()
    root.title("MOESI SIMULATOR")
    root.geometry("1500x750+5+5")
    MainWindow(root)
    root.mainloop()
