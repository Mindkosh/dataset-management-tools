import os
import time
import utils
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image, ImageEnhance
from labelDraw import LabelDraw
from tkinter import ttk
import random
import tkinter as tk


class AutoScrollbar(ttk.Scrollbar):

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')


class ImageCanvas:
    def __init__(self, ws, ws1, canvas_height, canvas_width, image_frame_indicator):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.image_frame_indicator = image_frame_indicator
        self.ws = ws1

        # Vertical and horizontal scrollbars for canvas
        vbar = AutoScrollbar(self.ws, orient='vertical')
        hbar = AutoScrollbar(self.ws, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=2, column=0, sticky='we')

        self.canvas = Canvas(
            self.ws,
            width=canvas_width,
            height=canvas_height,
            xscrollcommand=hbar.set,
            yscrollcommand=vbar.set
        )
        self.click = False
        self.canvas.grid(row=0, column=0)
        # self.ws.bind('<Configure>', self.onResize)
        # self.canvas_height = self.ws.winfo_reqheight()
        # self.canvas_width = self.ws.winfo_reqwidth()
        self.extension_list = [".png", ".jpg", ".jpeg"]
        self.imgs = []
        self.label_object = None
        self.img_index = 0

        if os.name == "nt":
            self.default_dataset_file = os.path.join(utils.get_assets_dir(),
                                                     "dataset\\annotations\\instances_default.json")
        else:
            self.default_dataset_file = os.path.join(utils.get_assets_dir(),
                                                     "dataset/annotations/instances_default.json")
        print(self.default_dataset_file)
        self.load_from_datumaro_dataset(self.default_dataset_file)
        vbar.configure(command=self.canvas.yview)  # bind scrollbars to the canvas
        hbar.configure(command=self.canvas.xview)
        
        

        self.ws.rowconfigure(0, weight=1)
        self.ws.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<ButtonPress-1>', self.move_from)
        self.canvas.bind('<B1-Motion>', self.move_to)
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>', self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>', self.wheel)  # only with Linux, wheel scroll up

        self.text = self.canvas.create_text(0, 0, anchor='nw', text='Scroll to zoom')

        self.imscale = 1.0  # scale for the canvas image
        self.delta = 0.75  # zoom magnitude
        self.imageid = None

        width, height = self.raw_img.size
        minsize, maxsize = 5, 20
        self.img_container = self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height, width=0)
        self.show_image()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        # self.y1,self.y2=self.canvas.yview()
        # self.x1,self.x2=self.canvas.xview()
        # print(self.canvas.yview())

    def wheel(self, event):
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.delta == -120:
            scale *= self.delta
            self.imscale *= self.delta
        if event.delta == 120:
            scale /= self.delta
            self.imscale /= self.delta
        # Rescale all canvas objects
        self.x = self.canvas.canvasx(event.x)
        self.y = self.canvas.canvasy(event.y)
        self.canvas.scale('all', self.x, self.y, scale, scale)
        self.show_image()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        #self.y1,self.y2=self.canvas.yview()
        #self.x1,self.x2=self.canvas.xview()

    def loadScale(self, scale, x, y):
        # Rescale all canvas objects
        self.imscale = scale
        self.x = self.canvas.canvasx(x)
        self.y = self.canvas.canvasy(y)
        self.canvas.scale('all', self.x, self.y, scale/self.delta, scale/self.delta)
        self.show_image()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def show_image(self, event=None):
        self.canvas.delete('all')
        if self.imageid:
            self.canvas.delete(self.imageid)
            self.imageid = None
            self.canvas.imagetk = None  # delete previous image from the canvas
        width, height = self.raw_img.size
        new_size = int(self.imscale * width), int(self.imscale * height)
        imagetk = ImageTk.PhotoImage(self.raw_img.resize(new_size))
        # Use self.text object to set proper coordinates
        self.imageid = self.canvas.create_image((0, 0), image=imagetk)
        # self.canvas.lower(self.imageid)  # set it into background
        self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

    def calc_size(self, size):
        if size[0] > size[1]:
            width = min(self.canvas_width, size[0])
            height = int((width / size[0]) * size[1])
        else:
            height = min(self.canvas_width, size[1])
            width = int((height / size[1]) * size[0])
        return [width, height]

    def next_image(self):
        self.canvas.delete('all')
        if self.img_index < self.number_of_images - 1:
            if self.imageid:
                self.canvas.delete(self.imageid)
                self.imageid = None
                self.canvas.imagetk = None  # delete previous image from the canvas
            if self.label_object is not None:
                self.raw_img = self.label_object.get_labeled_image(self.img_index + 1)
            else:
                self.raw_img = Image.open(self.imgs[self.img_index + 1])
            self.w, self.h = self.raw_img.size
            self.canvas.config(width=self.w, height=self.h)
            self.img_index = self.img_index + 1
            self.show_image()
            self.image_frame_indicator.set(str(self.img_index + 1) + "/" + str(self.number_of_images))
            # if self.label_object is not None:
            #     self.raw_img = self.label_object.get_labeled_image(self.img_index+1)
            # else:
            #     self.raw_img = Image.open( self.imgs[self.img_index+1] )

            # self.w, self.h = self.calc_size( self.raw_img.size )
            # self.raw_img = self.raw_img.resize((self.w, self.h), Image.ANTIALIAS)
            # self.new_img = ImageTk.PhotoImage( self.raw_img )

            # self.canvas.itemconfig( self.img_container, image=self.new_img )
            # self.canvas.config(width=self.w, height=self.h)
            # self.img_index+=1
            # self.image_frame_indicator.set( str(self.img_index+1) + "/" + str(self.number_of_images))

    def previous_image(self):
        self.canvas.delete('all')
        if self.img_index > 0:
            if self.imageid:
                self.canvas.delete(self.imageid)
                self.imageid = None
                self.canvas.imagetk = None  # delete previous image from the canvas
            if self.label_object is not None:
                self.raw_img = self.label_object.get_labeled_image(self.img_index - 1)
            else:
                self.raw_img = Image.open(self.imgs[self.img_index - 1])

            self.w, self.h = self.calc_size(self.raw_img.size)
            self.raw_img = self.raw_img.resize((self.canvas_width, self.canvas_height), Image.ANTIALIAS)
            self.new_img = ImageTk.PhotoImage(self.raw_img)

            self.canvas.itemconfig(self.canvas.create_image(0, 0, image=self.new_img, anchor=NW), image=self.new_img)
            self.canvas.config(width=self.w, height=self.h)
            self.img_index -= 1
            self.image_frame_indicator.set(str(self.img_index + 1) + "/" + str(self.number_of_images))

    def update_img_list(self, img_list=None):
        if img_list is None:
            print("none")
            self.img_dir = filedialog.askdirectory(title="Select Image Directory", initialdir=os.getcwd())
            if self.img_dir == ():
                return

            self.imgs = []
            for i in os.listdir(self.img_dir):
                if os.path.splitext(i)[-1] in self.extension_list:
                    self.imgs.append(os.path.join(self.img_dir, i))
            self.label_object = None

        else:
            self.imgs = img_list

        self.img_index = 0
        self.number_of_images = len(self.imgs)

        if self.number_of_images > 0:
            if img_list is not None and self.label_object is not None:
                self.raw_img = self.label_object.get_labeled_image(0)
            else:
                self.raw_img = Image.open(self.imgs[0])

            self.w, self.h = self.calc_size(self.raw_img.size)
            self.raw_img = self.raw_img.resize((self.w, self.h), Image.ANTIALIAS)
            self.base_img = ImageTk.PhotoImage(self.raw_img)
            self.canvas.config(width=self.w, height=self.h)
            self.img_container = self.canvas.create_image(
                0,
                0,
                anchor=NW,
                image=self.base_img
            )
            self.canvas.delete(self.img_container)
            self.image_frame_indicator.set(str(self.img_index + 1) + "/" + str(self.number_of_images))

        return [True, img_list]

    def load_from_datumaro_dataset(self, filename=None):
        if filename is None:
            # labels_file = "/home/sdevgupta/tests/hh2/annotations/instances_default.json"
            labels_file = filedialog.askopenfile(mode='r', filetypes=[('JSON Files', '*.json')],
                                                 title="Select Dataset file", initialdir=os.getcwd()).name
        else:
            labels_file = filename

        try:
            self.label_object = LabelDraw(labels_file)
            img_list = self.label_object.get_image_list()
            self.update_img_list(img_list)
        except Exception as e:
            print(e)
            messagebox.showinfo("Error", "Could not parse Labels file")

    def export_images_with_labels(self, progress_bar):
        for index in range(self.number_of_images):
            labeled_img = self.label_object.get_labeled_image(index)

            if os.name == "nt":
                if not os.path.exists(os.path.join(utils.get_assets_dir(), "dataset\\exports")):
                    os.mkdir(os.path.join(utils.get_assets_dir(), "dataset\\exports"))
                output_path = os.path.join(utils.get_assets_dir(), "dataset\\exports",
                                           os.path.basename(self.imgs[index]))
            else:
                if not os.path.exists(os.path.join(utils.get_assets_dir(), "dataset/exports")):
                    os.mkdir(os.path.join(utils.get_assets_dir(), "dataset/exports"))
                output_path = os.path.join(utils.get_assets_dir(), "dataset/exports",
                                           os.path.basename(self.imgs[index]))
            labeled_img.save(output_path)
            # Update progress bar
            time.sleep(1)
            progress_bar['value'] += int(200 * float(index + 1) / self.number_of_images)
            self.ws.update_idletasks()
        return True

    # def resetSize(self):
    #     print(self.canvas_width, self.canvas_height)
    #     self.raw_img = self.raw_img.resize((self.canvas_width - 50, self.canvas_height - 50), Image.ANTIALIAS)
    #     self.new_img = ImageTk.PhotoImage(self.raw_img)
    #
    #     self.canvas.config(width=self.canvas_width, height=self.canvas_height)

    def onResize(self, event):
        print(event.width, event.height)
        # resize the canvas
        img = Image.open(self.imgs[self.img_index])
        resized = img.resize((event.width, event.height), Image.ANTIALIAS)
        img2 = ImageTk.PhotoImage(resized)
        self.canvas.create_image(0, 0, image=img2, anchor='nw')

    def control(self, n):
        m = float(n)
        self.raw_img = self.label_object.get_labeled_image(self.img_index)
        enhancer = ImageEnhance.Brightness(self.raw_img)
        im = enhancer.enhance(m)
        self.raw_img = im
        img2 = ImageTk.PhotoImage(im)
        image_on_canvas = self.canvas.create_image(0, 0, image=img2, anchor=NW)
        self.canvas.itemconfig(image_on_canvas, image=img2)
        self.show_image()

    def updateImage(self, img_index):
        self.canvas.delete('all')
        if self.label_object is not None:
            self.raw_img = self.label_object.get_labeled_image(img_index)
        else:
            self.raw_img = Image.open(self.imgs[img_index])

        new_size = int(self.imscale * self.raw_img.width), int(self.imscale * self.raw_img.height)
        self.raw_img = self.raw_img.resize(new_size, Image.ANTIALIAS)
        self.new_img = ImageTk.PhotoImage(self.raw_img)

        self.canvas.itemconfig(self.canvas.create_image((0, 0), image=self.new_img), image=self.new_img)
        self.canvas.config(width=self.w, height=self.h)
        self.img_index = img_index
        self.image_frame_indicator.set(str(img_index+1) + "/" + str(self.number_of_images))

    def getImgList(self):
        return self.imgs

    def load_polygon(self):
        if os.name == "nt":
            self.default_dataset_file = os.path.join(utils.get_assets_dir(),
                                                     "dataset\\annotations\\instances_default_polygon.json")
        else:
            self.default_dataset_file = os.path.join(utils.get_assets_dir(),
                                                     "dataset/annotations/instances_default_polygon.json")
        print(self.default_dataset_file)
        self.load_from_datumaro_dataset(self.default_dataset_file)

    def load_polyline(self):
        if os.name == "nt":
            self.default_dataset_file = os.path.join(utils.get_assets_dir(),
                                                     "dataset\\annotations\\instances_default_polyline.json")
        else:
            self.default_dataset_file = os.path.join(utils.get_assets_dir(),
                                                     "dataset/annotations/instances_default_polyline.json")
        print(self.default_dataset_file)
        self.load_from_datumaro_dataset(self.default_dataset_file)

    def colorPicker(self, m):
        col = (hex(int(m))).split('x')[1]
        if len(col) != 6 and col != '0':
            col = '0' + col
        self.raw_img = self.label_object.get_labeled_image(self.img_index, outline="#" + col if col is not '0' else '#000')
        img2 = ImageTk.PhotoImage(self.raw_img)
        image_on_canvas = self.canvas.create_image(0, 0, image=img2, anchor=NW)
        self.canvas.itemconfig(image_on_canvas, image=img2)
        self.show_image()
