import os
import time
from tkinter import * 
import tkinter.font as font
from tkinter.ttk import Progressbar
from imageCanvas import ImageCanvas
import utils

class MainWindow:

    def __init__(self):
        self.ws = Tk()
        self.height = min(1200, self.ws.winfo_screenwidth())
        self.width = min(900, self.ws.winfo_screenheight())

        self.ws.title('Explore Dataset')
        self.ws.tk.call('wm', 'iconphoto', self.ws._w, PhotoImage(file=os.path.join(utils.get_assets_dir(), 'logo_transparent.png') ))

        self.controlsFrame = Frame(self.ws, borderwidth=1, pady=10)
        self.controlsFrame.grid(row=1, column=0)

        self.image_number = StringVar()
        self.image_number.set("0/0")
        self.image_number_label = Label( self.controlsFrame, textvariable=self.image_number, font=("Arial", 16), pady=8, padx=10 )
        
        self.image_number_label.grid(row=0, column=1)
        
        self.imageFrame = Frame(self.ws, relief=RAISED, borderwidth=1)
        self.imageFrame.grid(row=0, column=0)
        self.canvas_obj = ImageCanvas(self.imageFrame, self.ws, self.height, self.width, self.image_number)

        self.myFont = font.Font(size=12)
        
        self.btn3 = Button(self.controlsFrame, text="Previous", command = self.canvas_obj.previous_image, bg='#0052cc', fg='#ffffff', pady=8, cursor="hand1" )
        self.btn3["font"] = self.myFont
        self.btn3.grid(row=0, column=0)
        
        self.btn4 = Button(self.controlsFrame, text="Next", command = self.canvas_obj.next_image, bg='#0052cc', fg='#ffffff', pady=8, cursor="hand1" )
        self.btn4["font"] = self.myFont
        self.btn4.grid(row=0, column=2)

        self.createMenu()


    def aboutWindow(self):
        print("Menu option clicked")
    

    def load_from_dataset_file(self):
        self.popup_bonus()
        self.ws.update()
        if self.canvas_obj.load_from_datumaro_dataset() is True:
            self.popup_window.destroy()
            self.filemenu.entryconfig( 2, state="normal")
            self.ws.update()


    def load_from_directory(self):
        # self.popup_bonus()
        # self.ws.update()
        # time.sleep(3)
        if self.canvas_obj.update_img_list() is True:
            self.filemenu.entryconfig( 2, state="disabled")
            self.ws.update()
            # self.popup_window.destroy()

    def export_labeled_images(self):
        self.popup_progress_bar()
        self.ws.update()
        if self.canvas_obj.export_images_with_labels( self.progress_bar ) is True:
            self.progress_bar_window.destroy()

    def settings_dialog(self):
        pass

    def createMenu(self):
        # Menu
        self.menubar = Menu(self.ws)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load from Dataset file", command=self.load_from_dataset_file, font=("Arial", 16))
        self.filemenu.add_command(label="Load Image Directory", command=self.load_from_directory, font=("Arial", 16))
        self.filemenu.add_command(label="Export Images with labels", command=self.export_labeled_images, font=("Arial", 16), state="normal")
        
        self.filemenu.add_separator()

        self.filemenu.add_command(label="Settings", command=self.settings_dialog, font=("Arial", 16), state="disabled")
        self.filemenu.add_command(label="Exit", command=self.ws.quit, font=("Arial", 16))
        self.menubar.add_cascade(label="File", menu=self.filemenu, font=("Arial", 16))
       
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About", command=self.aboutWindow, font=("Arial", 16))
        self.menubar.add_cascade(label="Help", menu=self.helpmenu, font=("Arial", 16))
        self.ws.config(menu=self.menubar)


    def popup_bonus(self):
        self.popup_window = Toplevel()
        
        self.popup_window.wm_title("Loading Data")
        
        self.popup_window_label = Label( self.popup_window, text="Loading Dataset...", padx=20, pady=20, font=("Arial", 16) )
        self.popup_window_label.grid(row=0, column=0)


    def popup_progress_bar(self):
        self.progress_bar_window = Toplevel()
        
        self.progress_bar_window.wm_title("Exporting")
        self.progress_window_label1 = Label( self.progress_bar_window, text="Exporting Labeled Images", padx=20, pady=20, font=("Arial", 16) )
        self.progress_window_label1.grid(row=0, column=0)
        
        self.progress_bar = Progressbar(
                                self.progress_bar_window,
                                orient = HORIZONTAL,
                                length = 200,
                                mode = 'determinate'
                            )
        self.progress_bar.grid( row=1, column=0 )
        self.progress_window_label2 = Label( self.progress_bar_window, text="", padx=20, pady=20, font=("Arial", 16) )
        self.progress_window_label2.grid(row=2, column=0)

    def run(self):
        self.ws.mainloop()


if __name__ == '__main__':
    main_window = MainWindow()
    main_window.run()
    