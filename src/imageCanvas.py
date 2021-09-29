import os
import time
import utils
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
from labelDraw import LabelDraw

class ImageCanvas:
    def __init__(self, ws, ws1, canvas_height, canvas_width, image_frame_indicator):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.image_frame_indicator = image_frame_indicator
        self.ws = ws1
        self.canvas = Canvas(
                        self.ws, 
                        width = canvas_width, 
                        height = canvas_height
                    )  
        self.canvas.grid(row=0, column=0)  

        self.extension_list = [".png", ".jpg", ".jpeg"]
        self.imgs = []
        self.img_dir = os.path.join( utils.get_assets_dir(), "dataset/images" )
        self.label_object = None

        for i in os.listdir(self.img_dir):
            if os.path.splitext(i)[-1] in self.extension_list:
                self.imgs.append( os.path.join(self.img_dir, i) )
        
        self.img_index = 0
        self.number_of_images = len(self.imgs)

        if self.number_of_images>0:
            self.raw_img = Image.open(self.imgs[0])
            self.w, self.h = self.calc_size( self.raw_img.size )
            self.raw_img = self.raw_img.resize((self.w, self.h), Image.ANTIALIAS)
            self.base_img = ImageTk.PhotoImage( self.raw_img )
            self.img_container = self.canvas.create_image(
                                0, 
                                0, 
                                anchor=NW, 
                                image=self.base_img
                            )
            self.canvas.config(width=self.w, height=self.h)
            self.image_frame_indicator.set( "1/" + str(self.number_of_images) )

        self.labels_file = ""


    def calc_size( self, size ):
        if size[0]>size[1]:
            width = min(self.canvas_width, size[0])
            height = int((width/size[0])*size[1])
        else:
            height = min(self.canvas_width, size[1])
            width = int((height/size[1])*size[0])
        
        return [width, height]


    def next_image(self):
        if self.img_index<self.number_of_images-1:
            if self.label_object is not None:
                self.raw_img = self.label_object.get_labeled_image(self.img_index+1)
            else:
                self.raw_img = Image.open( self.imgs[self.img_index+1] )

            self.w, self.h = self.calc_size( self.raw_img.size )
            self.raw_img = self.raw_img.resize((self.w, self.h), Image.ANTIALIAS)
            self.new_img = ImageTk.PhotoImage( self.raw_img )

            self.canvas.itemconfig( self.img_container, image=self.new_img )
            self.canvas.config(width=self.w, height=self.h)
            self.img_index+=1
            self.image_frame_indicator.set( str(self.img_index+1) + "/" + str(self.number_of_images))
    

    def previous_image(self):
        if self.img_index>0:
            if self.label_object is not None:
                self.raw_img = self.label_object.get_labeled_image(self.img_index-1)
            else:
                self.raw_img = Image.open( self.imgs[self.img_index-1] )

            self.w, self.h = self.calc_size( self.raw_img.size )
            self.raw_img = self.raw_img.resize((self.w, self.h), Image.ANTIALIAS)
            self.new_img = ImageTk.PhotoImage( self.raw_img )

            self.canvas.itemconfig( self.img_container, image=self.new_img )
            self.canvas.config(width=self.w, height=self.h)
            self.img_index-=1
            self.image_frame_indicator.set( str(self.img_index+1) + "/" + str(self.number_of_images))
        

    def update_img_list(self, img_list=None):
        if img_list is None:
            self.img_dir = filedialog.askdirectory(title="Select Image Directory", initialdir=os.getcwd())
            if self.img_dir==():
                return

            self.imgs = []
            for i in os.listdir(self.img_dir):
                if os.path.splitext(i)[-1] in self.extension_list:
                    self.imgs.append( os.path.join(self.img_dir, i) )
            self.label_object = None

        else:
            self.imgs = img_list

        self.img_index = 0
        self.number_of_images = len(self.imgs)
        
        if self.number_of_images>0:
            if img_list is not None and self.label_object is not None:
                self.raw_img = self.label_object.get_labeled_image(0)
            else:
                self.raw_img = Image.open(self.imgs[0])

            self.w, self.h = self.calc_size( self.raw_img.size )
            self.raw_img = self.raw_img.resize((self.w, self.h), Image.ANTIALIAS)
            self.base_img = ImageTk.PhotoImage( self.raw_img )
            self.canvas.config(width=self.w, height=self.h)
            self.img_container = self.canvas.create_image(
                                0, 
                                0, 
                                anchor=NW, 
                                image=self.base_img
                            )
            self.image_frame_indicator.set( str(self.img_index+1) + "/" + str(self.number_of_images))
        
        return True
                

    def load_from_datumaro_dataset(self):
        # labels_file = filedialog.askopenfile(mode ='r', filetypes =[('JSON Files', '*.json')], title="Select Dataset file", initialdir=os.getcwd()).name
        labels_file = "/home/sdevgupta/Downloads/task_sdsd-2021_08_25_12_43_26-coco 1.0/annotations/instances_default.json"

        try:
            self.label_object = LabelDraw( labels_file )
            img_list = self.label_object.get_image_list()
            self.update_img_list(img_list)
        except Exception as e:
            print(e)
            messagebox.showinfo("Error", "Could not parse Labels file")
        
        return True

    def export_images_with_labels(self, progress_bar):
        for index in range( self.number_of_images ):
            labeled_img = self.label_object.get_labeled_image(index)
            output_path = os.path.join( utils.get_assets_dir(), "dataset/exports", os.path.basename(self.imgs[index]))
            labeled_img.save( output_path )
            # Update progress bar
            time.sleep(1)
            progress_bar['value'] += int( 200*float(index+1)/self.number_of_images )
            self.ws.update_idletasks()
        return True