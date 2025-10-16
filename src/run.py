import os
from tkinter import *
import tkinter.font as font
from PIL import Image
from tkinter.ttk import Progressbar
from imageCanvas import ImageCanvas
import utils
from gallery import Gallery
from tkinter import filedialog
import json

class MainWindow:

    def __init__(self):
        self.ws = Tk()
        self.img_list = []

        self.width = self.ws.winfo_screenwidth()-50
        self.height = self.ws.winfo_screenheight()-130

        self.ws.title('Browse image datasets')
        self.ws.geometry(
            "%dx%d+0+0" % (self.ws.winfo_screenwidth(), self.ws.winfo_screenheight()))
        self.ws.configure(bg='#CBC9AD')
        self.ws.tk.call('wm', 'iconphoto', self.ws._w,
                        PhotoImage(file=os.path.join(utils.get_assets_dir(), 'favicon.png')))

        self.controlsFrame = Frame(
            self.ws, borderwidth=1, pady=30, padx=30, bg='#CBC9AD')
        self.controlsFrame.grid(row=1, column=0)

        self.image_number = StringVar()
        self.image_number.set("0/0")
        self.image_number_label = Label(self.controlsFrame, textvariable=self.image_number, font=("Arial", 15), bg='#CBC9AD', pady=8,
                                        padx=10)

        self.image_number_label.grid(row=0, column=1)

        self.canvas_obj = ImageCanvas(
            self.ws, self.height, self.width, self.image_number)

        self.myFont = font.Font(family="Helvetica", size=12)

        self.btn3 = Button(self.controlsFrame, text="Previous", command=self.canvas_obj.previous_image, bg='#656839',
                           fg='#ffffff', font=self.myFont, pady=8, cursor="hand1")
        self.btn3.grid(row=0, column=0)

        self.btn4 = Button(self.controlsFrame, text="Next", command=self.canvas_obj.next_image, bg='#656839',
                           fg='#ffffff', font=self.myFont, pady=8, cursor="hand1")
        self.btn4.grid(row=0, column=2)
        
        # self.btn5 = Button(self.controlsFrame, text="View Gallery", command=self.runGallery, bg='#656839',
        #                    fg='#ffffff', pady=8, cursor="hand1")
        # self.btn5["font"] = self.myFont
        # self.btn5.grid(row=0, column=3, padx=30)

        self.createMenu()
        self.v = DoubleVar()
        self.v1 = DoubleVar()
        self.scroll = Scale(self.controlsFrame, orient=HORIZONTAL, resolution=0.1, label='Brightness', font=self.myFont, from_=0, to=2,
                            variable=self.v, command=self.canvas_obj.control, bg='#CBC9AD')
        self.scroll.set(1)
        self.scroll.grid(row=0, column=4, padx=10)

        self.scroll1 = Scale(self.controlsFrame, orient=HORIZONTAL, resolution=1000, label='Color', font=self.myFont, from_=0, to=16777215,
                             variable=self.v1, command=self.canvas_obj.colorPicker, bg='#CBC9AD')
        self.scroll1.set(16711680)
        self.scroll1.grid(row=0, column=5, padx=10)

    def selectImage(self, img_index):
        self.canvas_obj.updateImage(img_index)

    def aboutWindow(self):
        print("Menu option clicked")
        print(self.controlsFrame.winfo_width(), self.controlsFrame.winfo_height())

    def runGallery(self):
        self.img_list = self.canvas_obj.getImgList()
        gallery = Gallery(self.img_list, self.selectImage)
        gallery.run()

    def load_from_dataset_file(self):
        self.popup_bonus()
        self.ws.update()
        self.img_list = self.canvas_obj.load_from_datumaro_dataset()
        
        if self.img_list and len(self.img_list) > 0:
            self.popup_window.destroy()
            self.filemenu.entryconfig(2, state="normal")
            self.ws.update()
            self.canvas_obj.img_index = 0
            self.canvas_obj.raw_img = self.canvas_obj.label_object.get_labeled_image(0)
            self.canvas_obj.show_image()
            self.canvas_obj.image_frame_indicator.set("1/" + str(self.canvas_obj.number_of_images))

    def load_from_directory(self):
        self.img_list = self.canvas_obj.update_img_list()
        if self.img_list[0] is True:
            self.filemenu.entryconfig(2, state="disabled")
            self.ws.update()

    def export_labeled_images(self):
        directory = filedialog.askdirectory(
            title='Select directory to export images', initialdir=os.getcwd())
        self.popup_progress_bar()
        self.ws.update()
        if self.canvas_obj.export_images_with_labels(self.progress_bar, directory) is True:
            self.progress_bar_window.destroy()

    def save_settings_dialog(self):
        y1, _ = self.canvas_obj.canvas.yview()
        x1, _ = self.canvas_obj.canvas.xview()
        settings_obj = {
            "image_brightness": self.scroll.get(),
            "zoom_scale": self.canvas_obj.imscale,
            "image_index": self.canvas_obj.img_index,
            "yview": y1,
            "xview": x1
        }
        with open("settings.json", "w") as outfile:
            json.dump(settings_obj, outfile)

    def loadSettings(self):
        f = open('settings.json')
        data = json.load(f)
        self.scroll.set(data['image_brightness'])
        self.canvas_obj.control(self.scroll.get())
        self.canvas_obj.updateImage(data['image_index'])
        self.canvas_obj.loadScale(data['zoom_scale'], 0, 0)
        self.canvas_obj.canvas.yview_moveto(data['yview'])
        self.canvas_obj.canvas.xview_moveto(data['xview'])

    def createMenu(self):
        # Menu
        self.menubar = Menu(self.ws)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load from Dataset file", command=self.load_from_dataset_file,
                                  font=("Arial", 12))
        self.filemenu.add_command(
            label="Load Image Directory", command=self.load_from_directory, font=("Arial", 12))
        self.filemenu.add_command(label="Export Images with labels", command=self.export_labeled_images,
                                  font=("Arial", 12), state="normal")

        self.filemenu.add_separator()

        self.filemenu.add_command(label="Save settings", command=self.save_settings_dialog, font=("Arial", 12),
                                  state="normal")
        self.filemenu.add_command(
            label="Exit", command=self.ws.quit, font=("Arial", 12))
        self.menubar.add_cascade(
            label="File", menu=self.filemenu, font=("Arial", 12))

        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(
            label="About", command=self.aboutWindow, font=("Arial", 12))
        self.menubar.add_cascade(
            label="Help", menu=self.helpmenu, font=("Arial", 12))

        self.annotationsmenu = Menu(self.menubar, tearoff=0)

        self.annotationsmenu.add_command(
            label="Bounding Box", command=self.canvas_obj.load_boundingbbox, font=("Arial", 12))

        self.annotationsmenu.add_command(
            label="Polyline", command=self.canvas_obj.load_polyline, font=("Arial", 12))

        self.annotationsmenu.add_command(
            label="Polygon", command=self.canvas_obj.load_polygon, font=("Arial", 12))

        self.menubar.add_cascade(
            label="Examples", menu=self.annotationsmenu, font=("Arial", 12))

        self.ws.config(menu=self.menubar)

    def popup_bonus(self):
        self.popup_window = Toplevel()

        self.popup_window.wm_title("Loading Data")
        self.popup_window_label = Label(self.popup_window, text="Loading Dataset...", padx=20, pady=20,
                                        font=("Arial", 15))
        self.popup_window_label.grid(row=0, column=0)

    def popup_progress_bar(self):
        self.progress_bar_window = Toplevel()

        self.progress_bar_window.wm_title("Exporting")
        self.progress_window_label1 = Label(self.progress_bar_window, text="Exporting Labeled Images", padx=20, pady=20,
                                            font=("Arial", 15))
        self.progress_window_label1.grid(row=0, column=0)

        self.progress_bar = Progressbar(
            self.progress_bar_window,
            orient=HORIZONTAL,
            length=200,
            mode='determinate'
        )
        self.progress_bar.grid(row=1, column=0)
        self.progress_window_label2 = Label(
            self.progress_bar_window, text="", padx=20, pady=20, font=("Arial", 15))
        self.progress_window_label2.grid(row=2, column=0)

    def run(self):
        self.ws.mainloop()


if __name__ == '__main__':
    main_window = MainWindow()
    main_window.run()
