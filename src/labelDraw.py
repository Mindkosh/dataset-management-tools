import os
import utils
import math
from tkinter import *
from PIL import Image, ImageDraw, ImageFont
from datumaro.components.dataset import Dataset
import cvat_format

class LabelDraw:
    def __init__(self, labels_file):
        if labels_file.endswith(".xml"):
            self.dataset = cvat_format.import_from(labels_file)
            self.dataset_type = "cvat"

            self.labels = self.dataset.labels
        else:
            try:
                self.dataset = Dataset.import_from(labels_file, 'coco')
                self.dataset_type = "coco"
            except Exception as e:
                try:
                    self.dataset = Dataset.import_from(labels_file, 'cvat')
                    self.dataset_type = "cvat"
                except Exception as e:
                    try:
                        self.dataset = Dataset.import_from(labels_file, 'voc')
                        self.dataset_type = "voc"
                    except Exception as e:
                        try:
                            self.dataset = Dataset.import_from(labels_file, 'mots')
                            self.dataset_type = "mots"
                        except Exception as e:
                            print(e)

            self.labels = [i.name for i in list(
                self.dataset.categories().values())[0]]
            
        self.annotations = []
        self.image_list = []
        for item in self.dataset:
            new_item = {}
            new_item["id"] = item.id
            
            if self.dataset_type == "cvat":
                self.image_list.append(os.path.join(utils.get_assets_dir(), "dataset_files\\images", os.path.basename(item.image.path)))
            else:
                self.image_list.append(item.image.path)

            new_item["label_items"] = []
            for i in item.annotations:
                label_item = {}
                label_item["points"] = i.points
                label_item["label_id"] = i.label
                label_item["label_name"] = self.labels[i.label]
                if hasattr(i, 'rotation'):
                    label_item["rotation"] = i.rotation
                new_item["label_items"].append(label_item)


            self.annotations.append(new_item)
        self.dataset = None

    def get_image_list(self):
        return self.image_list

    def distance(self, ax, ay, bx, by):
        return math.sqrt((by - ay)**2 + (bx - ax)**2)
    
    # rotates point `A` about point `B` by `angle` radians clockwise.
    def rotated_about(self, points, angle):
        
        centroid_x = (points[0] + points[2])/2
        centroid_y = (points[1] + points[3])/2

        rectangle_points = [
            (points[2], points[3]),
            (points[0], points[3]),
            (points[0], points[1]),
            (points[2], points[1]),
        ]
        
        polygon_points = []
        for i in rectangle_points:
            radius = self.distance(i[0], i[1], centroid_x, centroid_y)
            new_angle = angle + math.atan2(i[1]-centroid_y, i[0]-centroid_x)
        
            polygon_points.append( (round(centroid_x + radius * math.cos(new_angle)),
            round(centroid_y + radius * math.sin(new_angle))))

        return polygon_points
    

    def get_labeled_image(self, image_index, outline='#f11'):

        font = ImageFont.truetype(os.path.join(
            utils.get_assets_dir(), "fonts/Assistant-SemiBold.ttf"), 15)
        img = Image.open(self.image_list[image_index])
        img1 = ImageDraw.Draw(img)

        for label in self.annotations[image_index]["label_items"]:
            text_points = [label["points"][0]]
            text_points.append(max(label["points"][1] - 20, 0))
            img1.text(text_points, label["label_name"], outline, font)

            if len(label["points"]) == 4:
                if("rotation" in label and label["rotation"] != 0):
                    rotated_points = self.rotated_about(label['points'], math.radians(label["rotation"]))
                    img1.line((rotated_points[0], rotated_points[1]), fill=outline, width=3)
                    img1.line((rotated_points[1], rotated_points[2]), fill=outline, width=3)
                    img1.line((rotated_points[2], rotated_points[3]), fill=outline, width=3)
                    img1.line((rotated_points[3], rotated_points[0]), fill=outline, width=3)
                else:
                    img1.rectangle(label["points"], outline=outline, width=3)
            else:
                img1.line(label["points"], fill=outline, width=3)

        return img
