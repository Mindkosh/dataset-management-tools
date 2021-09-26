import os
from tkinter import * 
import tkinter.font as font
from imageCanvas import ImageCanvas
import utils

class MainWindow:

    def __init__(self):
        self.ws = Tk()
        self.height = 1500
        self.width = 1500
        self.ws.title('Explore Dataset')
        self.ws.tk.call('wm', 'iconphoto', self.ws._w, PhotoImage(file=os.path.join(utils.get_assets_dir(), 'logo_transparent.png') ))

        self.image_number = StringVar()
        self.image_number.set("0/0")
        self.image_number_label = Label( self.ws, textvariable=self.image_number, font=("Arial", 16), pady=8 )
        
        self.image_number_label.grid(row=1, column=3)
        
        self.canvas_obj = ImageCanvas(self.ws, self.height, self.width, self.image_number)

        self.myFont = font.Font(size=12, weight='bold')

        self.btn1 = Button(self.ws, text="Load from dataset file", command = self.canvas_obj.load_from_datumaro_dataset, bg='#0052cc', fg='#ffffff', pady=8, cursor="hand1" )
        self.btn1["font"] = self.myFont
        self.btn1.grid(row=1, column=0)

        self.btn2 = Button(self.ws, text="Load Image Directory", command = self.canvas_obj.update_img_list, bg='#0052cc', fg='#ffffff', pady=8, cursor="hand1" )
        self.btn2["font"] = self.myFont
        self.btn2.grid(row=1, column=1)

        self.btn3 = Button(self.ws, text="Previous", command = self.canvas_obj.previous_image, bg='#0052cc', fg='#ffffff', pady=8, cursor="hand1" )
        self.btn3["font"] = self.myFont
        self.btn3.grid(row=1, column=2)
        
        self.btn4 = Button(self.ws, text="Next", command = self.canvas_obj.next_image, bg='#0052cc', fg='#ffffff', pady=8, cursor="hand1" )
        self.btn4["font"] = self.myFont
        self.btn4.grid(row=1, column=4)

        self.ws.mainloop()

if __name__ == '__main__':
    main_window = MainWindow()
    