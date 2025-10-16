import os
import utils
import math
from tkinter import *
from PIL import Image, ImageDraw, ImageFont
from datumaro.components.dataset import Dataset
import cvat_format
import random
import consts

class LabelDraw:
    def __init__(self, labels_file):
        self._label_colors = {}
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
                            self.dataset = Dataset.import_from(
                                labels_file, 'mots')
                            self.dataset_type = "mots"
                        except Exception as e:
                            print(e)

            self.labels = [i.name for i in list(
                self.dataset.categories().values())[0]]

        self.annotations = []
        self.image_list = []
        self.label_list = {}
        for item in self.dataset:
            new_item = {}
            new_item["id"] = item.id
            if self.dataset_type == "cvat":
                alt1 = os.path.join(utils.get_assets_dir(
                ), "dataset_files\\images", os.path.basename(item.image.path))
                alt2 = os.path.join(os.path.dirname(
                    labels_file), "images", os.path.basename(item.image.path))
                img_filepath = alt1
                if os.path.exists(alt1) is False:
                    img_filepath = alt2

                self.image_list.append(img_filepath)
            else:
                self.image_list.append(item.image.path)

            new_item["label_items"] = []
            for ind,i in enumerate(item.annotations):
                label_item = {}
                label_item["points"] = i.points
                label_item["label_id"] = i.label
                label_item["label_name"] = self.labels[i.label]
                if hasattr(i, 'rotation'):
                    label_item["rotation"] = i.rotation
                new_item["label_items"].append(label_item)
                ann_type = i.type.name
                label_item["type"] = ann_type

                if label_item["label_id"] not in self._label_colors:
                    new_color = consts.colors[ind]
                    self._label_colors[label_item["label_id"]] = new_color
                    self.label_list[label_item["label_name"]] = [ann_type, new_color]

            self.annotations.append(new_item)
        self.dataset = None

    def get_label_list(self):
        return self.label_list

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

            polygon_points.append((round(centroid_x + radius * math.cos(new_angle)),
                                   round(centroid_y + radius * math.sin(new_angle))))

        return polygon_points

    def get_labeled_image(self, image_index, colorParam=None):
        font = ImageFont.truetype(os.path.join(
            utils.get_assets_dir(), "fonts/Assistant-SemiBold.ttf"), 15)
        img = Image.open(self.image_list[image_index])
        img1 = ImageDraw.Draw(img)

        for ind, label in enumerate(self.annotations[image_index]["label_items"]):

            label_id = label.get("label_id")
            if label_id not in self._label_colors:
                self._label_colors[label_id] = consts.colors[ind]

            if colorParam == None:
                color = self._label_colors[label_id]
            else:
                color = colorParam

            text_points = (label["points"][0], max(label["points"][1] - 20, 0))

            if label["type"] == 'bbox':
                if ("rotation" in label and label["rotation"] != 0):
                    rotated_points = self.rotated_about(
                        label['points'], math.radians(label["rotation"]))
                    img1.line(
                        (rotated_points[0], rotated_points[1]), fill=color, width=3)
                    img1.line(
                        (rotated_points[1], rotated_points[2]), fill=color, width=3)
                    img1.line(
                        (rotated_points[2], rotated_points[3]), fill=color, width=3)
                    img1.line(
                        (rotated_points[3], rotated_points[0]), fill=color, width=3)
                else:
                    img1.rectangle(label["points"], outline=color, width=3)

            elif label["type"] == 'polyline':
                cord_points = []
                for i in range(0, len(label['points']) - 1, 2):
                    x = label['points'][i]
                    y = label['points'][i + 1]
                    cord_points.append([x, y])
                for i in range(len(cord_points)-1):
                    img1.line((cord_points[i][0], cord_points[i][1], cord_points[i+1]
                              [0], cord_points[i+1][1]), fill=color, width=4)

            elif label["type"] == 'points':
                r = 3
                x = label['points'][0]
                y = label['points'][1]
                img1.ellipse((x - r, y - r, x + r, y + r), fill=color)

            img1.text(text_points, label["label_name"], color, font)

        return img
