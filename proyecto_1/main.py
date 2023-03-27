from tkinter import *
from tkinter import ttk
from cpu_core import CpuCore


class MainWindow():
    def __init__(self, root):
        super().__init__()

        # Tkinter frames
        root_frame = ttk.Frame(root)
        buttons_frame = ttk.Frame(root_frame, padding= "30 30 30 30")
        cpu_tables_frame = ttk.Frame(root_frame, padding= "100 0 0 0")

        self.cores = 4
        self.cpu_list = []
        self.cpu_table_list = []

        self.cpu_table_headers = ('state', 'dir', 'index', 'data')
        self.cpu_table_headers_text = ('State', 'Dir', 'Index', 'Data')

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
            cpu_title_labels.append(ttk.Label(cpu_tables_frame, text='N'+str(i), font = "Arial 16 bold"))
            self.cpu_table_list.append(ttk.Treeview(
                cpu_tables_frame, columns=self.cpu_table_headers, height=4))

        # Creating Cpu cores
        for i in range(self.cores):
            self.cpu_list.append(CpuCore(
                self.cpu_table_list[i], self.current_instr_list[i], self.bus_msgs_list[i]))
            # First column block
            self.cpu_table_list[i].column('#0', width=60)
            self.cpu_table_list[i].heading('#0', text='Block')

            for e in range(self.cores):
                # Columns ['0=State', '1=Dir', '2=Index', '3=Data']
                self.cpu_table_list[i].column(
                    self.cpu_table_headers[e], width=45, anchor='center')
                self.cpu_table_list[i].heading(
                    self.cpu_table_headers[e], text=self.cpu_table_headers_text[e])

        # Initialize Cpu cores data with default values
        for i in range(self.cores):
            self.cpu_table_list[i].insert(
                '', 'end', 'b0', text='B0', values=('I', '000', '0', '0000'))
            self.cpu_table_list[i].insert(
                '', 'end', 'b1', text='B1', values=('I', '000', '0', '0000'))
            self.cpu_table_list[i].insert(
                '', 'end', 'b2', text='B2', values=('I', '000', '1', '0000'))
            self.cpu_table_list[i].insert(
                '', 'end', 'b3', text='B3', values=('I', '000', '1', '0000'))

        # Positioning frames
        root_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        buttons_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        cpu_tables_frame.grid(column=0, row=1)

        self.button_start.grid(column=0, row=0)
        self.button_next.grid(column=1, row=0)
        self.button_stop.grid(column=2, row=0)

        # Positioning Cpu cores tables
        for i in range(self.cores):
            cpu_title_labels[i].grid(column=i, row=0)
            self.cpu_table_list[i].grid(
                column=i, row=1, padx=15, pady=5, columnspan=1)

    def start():
        pass

    def next():
        pass

    def stop():
        pass


if __name__ == "__main__":
    root = Tk()
    root.title("MOESI SIMULATOR")
    root.geometry("1400x750+5+5")
    MainWindow(root)
    root.mainloop()
