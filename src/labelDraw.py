import os
import utils
from tkinter import * 
from PIL import Image, ImageDraw, ImageFont
from datumaro.components.dataset import Dataset

class LabelDraw():
    def __init__( self, labels_file ):
        
        self.dataset = Dataset.import_from(labels_file, 'coco')
        self.labels = [i.name for i in list(self.dataset.categories().values())[0]]
        self.annotations = []
        self.image_list = []
        for item in self.dataset:
            new_item = {}
            new_item["id"] = item.id
            self.image_list.append(item.image.path)

            new_item["label_items"] = []
            for i in item.annotations:
                label_item = {}
                label_item["points"] = i.points
                label_item["label_id"] = i.label
                label_item["label_name"] = self.labels[i.label]
                new_item["label_items"].append(label_item)

            self.annotations.append(new_item)

        self.dataset = None
        
    
    def get_image_list(self):
        return self.image_list

    def get_labeled_image(self, image_index):
        font = ImageFont.truetype(os.path.join(utils.get_assets_dir(), "Assistant-VariableFont_wght.ttf"), 20)
        img = Image.open( self.image_list[image_index] )
        img1 = ImageDraw.Draw(img)

        for label in self.annotations[image_index]["label_items"]:
            text_points = [label["points"][0]]
            text_points.append(max(label["points"][1]-25, 0))
            img1.text( text_points, label["label_name"], (255,255,255), font=font, stroke_width=1)

            if len(label["points"])==4:
                img1.rectangle( label["points"], outline="#f11", width = 2)
            else:
                for idx in range(len(label["points"])):
                    img1.line( [label["points"][idx], label["points"][(idx+1)%len(label["points"])]], fill ="#f11", width = 2)

        return img


    
