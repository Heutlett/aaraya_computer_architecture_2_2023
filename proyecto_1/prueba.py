from tkinter import *
from PIL import ImageTk, Image

root = Tk()

image = Image.open("bus_img.jpg")
photo = ImageTk.PhotoImage(image)

label = Label(root, image=photo)
label.pack()

root.mainloop()
