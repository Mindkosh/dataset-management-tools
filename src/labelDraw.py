import os
import utils
import math
from PIL import ImageFont


class LabelDraw:
    def __init__(self, lineWidth=3, lineColor="#f11"):
        self.lineWidth = lineWidth
        self.lineColor = lineColor

    def updateLineColor(color):
        self.lineColor = color

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

    def get_labeled_image(self, img1, annotations, outline='#f11'):

        font = ImageFont.truetype(os.path.join(
            utils.get_assets_dir(), "fonts/Assistant-SemiBold.ttf"), 15)

        for label in annotations["label_items"]:
            text_points = [label["points"][0]]
            text_points.append(max(label["points"][1] - 20, 0))
            img1.text(text_points, label["label_name"], outline, font)

            if len(label["points"]) == 4:
                if ("rotation" in label and label["rotation"] != 0):
                    rotated_points = self.rotated_about(
                        label['points'], math.radians(label["rotation"]))
                    img1.line(
                        (rotated_points[0], rotated_points[1]), fill=self.outline, width=self.lineWidth)
                    img1.line(
                        (rotated_points[1], rotated_points[2]), fill=self.outline, width=self.lineWidth)
                    img1.line(
                        (rotated_points[2], rotated_points[3]), fill=self.outline, width=self.lineWidth)
                    img1.line(
                        (rotated_points[3], rotated_points[0]), fill=self.outline, width=self.lineWidth)
                else:
                    img1.rectangle(label["points"],
                                   outline=outline, width=self.lineWidth)
            else:
                img1.line(label["points"], fill=self.outline,
                          width=self.lineWidth)

        return img
