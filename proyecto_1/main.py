from time import sleep
from tkinter import *
from tkinter import ttk
from src.cpu_core import CpuController
from PIL import Image, ImageTk
from src.main_mem import MainMem
import src.utils
import threading as thread
import queue
from src.bus import Bus

class MainWindow():
    def __init__(self, root):
        super().__init__()
        
        self.root = root
        
        # Processor and memory frequency
        self.cpu_freq = 0.4
        self.mem_freq = self.cpu_freq + self.cpu_freq*0.4
        
        # Flag running
        self.playing = False

        # Styles
        style = ttk.Style()
        style.configure("White.TFrame", background="white")
        style.configure("Blue.TFrame", background="SkyBlue2")
        style.configure("Azure.TFrame", background="LightBlue1")

        # Tkinter frames
        root_frame = ttk.Frame(root, style="White.TFrame")
        buttons_frame = ttk.Frame(root_frame, style="White.TFrame", padding="0 10 0 10")
        tables_frame = ttk.Frame(root_frame, style="White.TFrame", padding="30 0 0 0")
        mem_frame = ttk.Frame(tables_frame, style="Blue.TFrame", padding="0 10 0 10")
        colors_ref_frame = ttk.Frame(tables_frame, style="Azure.TFrame", padding="0 0 0 0")

        # System variables
        self.cores = 4
        self.main_mem_blocks = 8
        self.cpu_list = []
        self.table_list = []
        self.bus_queue = queue.Queue()

        # Headers cache cpu tree_views
        self.cpu_table_headers = ('state', 'tag', 'index', 'data')
        self.cpu_table_headers_text = ('State', 'Tag', 'Index', 'Data')

        # Instructions variables
        self.current_instr_list = []
        self.next_instr_list = []
        self.bus_msgs_list = []
        self.next_instr_entry_text = StringVar()
        
        # Images for buttons
        self.start_image = ImageTk.PhotoImage(Image.open('imgs/play_button.png')
            .resize((130,50), Image.ANTIALIAS))
        self.stop_image = ImageTk.PhotoImage(Image.open('imgs/stop_button.png')
            .resize((130,50), Image.ANTIALIAS))
        self.next_image = ImageTk.PhotoImage(Image.open('imgs/next_button.png')
            .resize((130,50), Image.ANTIALIAS))

        # Buttons
        self.button_start = ttk.Button(
            buttons_frame, text='Play', image=self.start_image, command=self.start)
        self.button_next = ttk.Button(
            buttons_frame, text='Next', image=self.next_image, command=self.next)
        self.button_stop = ttk.Button(
            buttons_frame, text='Stop', image=self.stop_image, command=self.stop)

        # Cpu cores widgets
        labels_cpu_title = []
        label_current_inst_title_list = []
        label_next_inst_title_list = []
        entries_next_instr_list = []
        label_current_inst_list = []
        labels_bus_list = []
        frames_cpu_list = []

        # Initialize Cpu core lists and TreeViews
        for i in range(self.cores):
            # Frame
            frames_cpu_list.append(ttk.Frame(tables_frame, style="Blue.TFrame", padding="0 0 0 10"))
            # Next insts
            self.next_instr_list.append(StringVar())
            label_next_inst_title_list.append(
                ttk.Label(frames_cpu_list[i], background="lavender", text='    Next instruction:                     ', font="Arial 12 bold"))
            entries_next_instr_list.append(ttk.Entry(
                frames_cpu_list[i], font="Arial 12", textvariable=self.next_instr_list[i], style="Custom.TEntry", width=25,))
            # Current insts
            self.current_instr_list.append(StringVar())
            label_current_inst_title_list.append(
                ttk.Label(frames_cpu_list[i], background="MistyRose2", text='    Current instruction:               ', font="Arial 12 bold"))
            label_current_inst_list.append(ttk.Label(
                frames_cpu_list[i], textvariable=self.current_instr_list[i], foreground='OrangeRed4', font="Arial 12", background="azure3", width=25))
            self.current_instr_list.append(StringVar())
            self.bus_msgs_list.append(StringVar())
            self.bus_msgs_list[i].set("No operation")
            # Widgets
            labels_cpu_title.append(
                ttk.Label(frames_cpu_list[i], foreground='white', background='SteelBlue4',text='                           P'+str(i) + '                           ', font="Arial 16 bold"))
            self.table_list.append(ttk.Treeview(
                frames_cpu_list[i], columns=self.cpu_table_headers, height=4))
            # Bus
            labels_bus_list.append(ttk.Label(
                tables_frame, textvariable=self.bus_msgs_list[i], font="Arial 12 bold", background="white", foreground="forest green", width=11))
            
        # Creating tree_view mem
        self.main_mem_table = ttk.Treeview(mem_frame, columns=(
            'address', 'data'), show='headings', height=self.main_mem_blocks)
        self.main_mem = MainMem(self.main_mem_table)
        self.table_list.append(self.main_mem_table)

        # Creating bus
        self.bus = Bus(self.main_mem.cache_tree_view, self.bus_queue, self.table_list, self.cores, self.mem_freq, self.cpu_freq)
        
        # Creating Cpu cores
        for i in range(self.cores):
            self.cpu_list.append(CpuController(
                i, self.table_list[i], self.current_instr_list[i], self.bus_msgs_list[i], self.bus_queue, self.cpu_freq))
            # First column block
            self.table_list[i].column('#0', width=60)
            self.table_list[i].heading('#0', text='Block')

            for e in range(4):
                # Columns ['0=State', '1=Dir', '2=Index', '3=Data']
                self.table_list[i].column(
                    self.cpu_table_headers[e], width=65, anchor='center')
                self.table_list[i].heading(
                    self.cpu_table_headers[e], text=self.cpu_table_headers_text[e])

        # Initialize Cpu cores data with default values
        for i in range(self.cores):
            self.table_list[i].insert(
                '', 'end', 'b0', text='B0', tags='b0', values=('I', '00', '0', '0000'))
            self.table_list[i].insert(
                '', 'end', 'b1', text='B1', tags='b1', values=('I', '00', '0', '0000'))
            self.table_list[i].insert(
                '', 'end', 'b2', text='B2', tags='b2', values=('I', '00', '1', '0000'))
            self.table_list[i].insert(
                '', 'end', 'b3', text='B3', tags='b3', values=('I', '00', '1', '0000'))

        # Creating mem tree_view 
        self.main_mem_table.column('address', width=70, anchor='center')
        self.main_mem_table.heading('address', text='Address')
        self.main_mem_table.column('data', width=70, anchor='center')
        self.main_mem_table.heading('data', text='Data')

        # Initializing mem blocks
        for i in range(self.main_mem_blocks):
            self.main_mem_table.insert(
                '', 'end', 'm'+str(i), text='M'+str(i), tags='m'+str(i), values=(src.utils.int_to_binary(i), '000'))

        # Positioning frames
        root_frame.grid(column=0, row=0)
        buttons_frame.grid(column=0, row=0)
        tables_frame.grid(column=0, row=1)
        
        # Positioning buttons
        self.button_start.grid(column=0, row=0, padx=5)
        self.button_next.grid(column=2, row=0, padx=25)
        self.button_stop.grid(column=1, row=0)
        self.button_stop.state(['disabled'])

        # Positioning Cpu cores tables
        for i in range(self.cores):
            frames_cpu_list[i].grid(column=i, row=0, padx=5)
            labels_cpu_title[i].grid(column=i, row=0, pady=10)

            label_next_inst_title_list[i].grid(column=i, row=1)
            entries_next_instr_list[i].grid(column=i, row=2,pady=5)
            label_current_inst_title_list[i].grid(column=i, row=3,pady=5)
            label_current_inst_list[i].grid(column=i, row=4)
            self.table_list[i].grid(
                column=i, row=5, padx=15, pady=5, columnspan=1)
            labels_bus_list[i].grid(column=i, row=6, pady=5)

        # Creating and positioning bus image
        bus_img = Image.open("imgs/bus_img.png")
        bus_img_tk = ImageTk.PhotoImage(bus_img)
        bus_img_label = ttk.Label(tables_frame, image=bus_img_tk)
        bus_img_label.image = bus_img_tk
        bus_img_label.grid(column=0, row=7, columnspan=4, pady=10)

        # Positioning main memory tables
        mem_title = ttk.Label(mem_frame, foreground='white', background='SteelBlue4',text='        Main Memory        ', font="Arial 16 bold")        
        mem_frame.grid(column=1, row=8, columnspan=2)
        mem_title.grid(column=0, row=0)
        self.main_mem_table.grid(column=0, row=1, pady=5)

        # Colors reference
        colors_ref_frame.grid(column=0, row=8)
        title_color_ref = ttk.Label(colors_ref_frame, foreground='white', background='SteelBlue4', width=20, text='Colors reference', font="Arial 10 bold")
        read_hit_color = ttk.Label(colors_ref_frame, foreground='black', width=20, background='medium spring green',text='Read hit', font="Arial 10 bold")
        read_miss_color = ttk.Label(colors_ref_frame, foreground='black', width=20, background='Salmon',text='Read miss', font="Arial 10 bold")
        read_after_miss_color = ttk.Label(colors_ref_frame, foreground='black', width=20, background='yellow',text='Read after miss', font="Arial 10 bold")
        write_miss_color = ttk.Label(colors_ref_frame, foreground='black', width=20, background='tan4',text='Write miss', font="Arial 10 bold")
        write_hit_color = ttk.Label(colors_ref_frame, foreground='black', width=20, background='DarkOrange1',text='Write hit', font="Arial 10 bold")
        write_after_miss = ttk.Label(colors_ref_frame, foreground='black', width=20, background='green2',text='Write after miss', font="Arial 9 bold")
        wb_mem_color = ttk.Label(colors_ref_frame, foreground='black', width=20, background='turquoise1',text='Write back', font="Arial 10 bold")
        found_in_cache_color = ttk.Label(colors_ref_frame, foreground='black', width=20, background='RoyalBlue1',text='Found (O, M) in other P', font="Arial 9 bold")
        found_in_mem_color = ttk.Label(colors_ref_frame, foreground='black', width=20, background='Magenta2',text='Found in mem', font="Arial 9 bold")
        to_invalidate_color = ttk.Label(colors_ref_frame, foreground='black', width=20, background='red',text='To invalidate', font="Arial 10 bold")
        title_color_ref.grid        (column=0, row=0, pady=5)
        read_hit_color.grid         (column=0, row=1, pady=2)
        read_miss_color.grid        (column=0, row=2, pady=2)
        read_after_miss_color.grid  (column=0, row=3, pady=2)
        write_hit_color.grid        (column=0, row=4, pady=2)
        write_miss_color.grid       (column=0, row=5, pady=2)
        write_after_miss.grid       (column=0, row=6, pady=2)
        wb_mem_color.grid           (column=0, row=7, pady=2)
        found_in_cache_color.grid   (column=0, row=8, pady=2)
        found_in_mem_color.grid     (column=0, row=9, pady=2)
        to_invalidate_color.grid    (column=0, row=10, pady=2)
        
        

    def put_new_instructions(self):
        threads = list()
        for i in range(self.cores):
            thread_i = thread.Thread(target=src.utils.set_next_instruction, args=(i,self.next_instr_list[i],))
            threads.append(thread_i)
            thread_i.start()

    def start(self):
        self.playing = True
        self.update_next()
        self.button_next.state(['disabled'])
        self.button_start.state(['disabled'])
        self.button_stop.state(['!disabled'])
        
    def update_next(self):
        if(self.playing):
            self.next_action()
            self.root.after(2000, self.update_next)

    def next(self):
        self.button_next.state(['!disabled'])
        self.button_start.state(['!disabled'])
        self.button_stop.state(['disabled'])
        self.next_action()

    def stop(self):
        self.playing = False
        self.root.after_cancel(self.update_next)
        self.button_next.state(['!disabled'])
        self.button_start.state(['!disabled'])
        self.button_stop.state(['disabled'])

    def next_action(self):
        threads = list()
        for i in range(self.cores):
            thread_i =  thread.Thread(target=self.cpu_list[i].process_instruction, args=(self.next_instr_list[i].get(),), 
                daemon=True)
            threads.append(thread_i)
            thread_i.start()
            
        sleep(0.3)
        self.put_new_instructions()
        
        thread_bus = thread.Thread(target=self.bus.process_bus_queue, args=())
        thread_bus.start()


if __name__ == "__main__":
    root = Tk()
    root.title("MOESI SIMULATOR")
    root.geometry("1500x750+5+5")
    root.configure(bg='white')
    MainWindow(root)
    root.mainloop()
