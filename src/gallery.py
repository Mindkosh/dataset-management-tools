import tkinter
import os
import utils
from PIL import ImageTk, Image


class Gallery:

    def __init__(self, img_list, selectImage):
        self.gallery = tkinter.Toplevel()
        self.selectImage = selectImage
        self.gallery.title('Image Gallery')
        self.imageFrame = tkinter.Frame(self.gallery)
        self.imageFrame.grid(row=0, column=0)
        self.vbar = tkinter.Scrollbar(self.gallery, orient='vertical')
        self.vbar.grid(row=0, column=3)
        # if img_list is not None:
        #     rows = int(len(img_list)/3) + 1
        #     for i in range(0, rows):
        #         for j, k in zip(range(0, 3), range(0, len(img_list))):
        #             print(i, j, k)
        #             self.imageFrame.append(tkinter.Frame(self.gallery, relief=tkinter.RAISED, borderwidth=1))
        #             self.imageFrame[k].grid(row=i, column=j)
        #             self.canvas_obj.append(tkinter.Canvas(
        #                 self.gallery,
        #                 width=100,
        #                 height=100,
        #             ))
        #             im = ImageTk.PhotoImage(Image.open(img_list[k]))
        #             self.image_canvas.append(self.canvas_obj[k].create_image(
        #                 20,
        #                 20,
        #                 image=im))
        #             self.canvas_obj[k].itemconfig(self.image_canvas[k], image=im)
        self.all_labels = []
        if img_list is not None:
            for i in range(len(img_list)):
                image = ImageTk.PhotoImage(Image.open(img_list[i]).resize((150, 100), Image.ANTIALIAS))
                label = tkinter.Button(self.imageFrame, image=image, command=lambda c=i: self.select(c))
                label.photo = image
                label.grid(row=int(i/3), column=i % 3)
                self.all_labels.append(label)

    def select(self, index):
        self.selectImage(index)
        self.gallery.destroy()

    def run(self):
        self.gallery.mainloop()
