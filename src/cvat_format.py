import xml.etree.ElementTree as ET


class Image:
    def __init__(self, name, path):
        self.name = name
        self.path = path


class AnnType:
    def __init__(self, name):
        self.name = name


class Annotation:
    def __init__(self, label_id, points, type, rotation=None):
        self.label = label_id
        self.points = points
        self.rotation = rotation if rotation else 0
        self.type = AnnType(type)


class DatasetItem:
    def __init__(self, id, annotations, image):
        self.id = id
        self.annotations = annotations
        self.image = image


class Dataset:
    def __init__(self):
        self.items = []
        self.labels = {}
        self.num = -1

    def __iter__(self):
        return self

    def __next__(self):
        if self.num == len(self.items)-1:
            raise StopIteration
        else:
            self.num += 1
            return self.items[self.num]

    def add_item(self, item):
        self.items.append(item)

    def set_labels(self, labels):
        self.labels = labels

    def find_label_id(self, label_name):
        for i in self.labels.keys():
            if self.labels[i] == label_name:
                return i
        return -1


def import_from(filename):
    annotation_tree = ET.parse(filename)
    root_annotations = annotation_tree.getroot()

    dataset = Dataset()
    labs = {}
    for child in root_annotations:
        if (child.tag == "meta"):
            for meta in child:
                if meta.tag == "task":
                    for detail in meta:
                        if detail.tag == "labels":
                            for ind, label in enumerate(detail):
                                for lab_attr in label:
                                    if lab_attr.tag == "name":
                                        labs[ind] = lab_attr.text

    dataset.set_labels(labs)

    for child in root_annotations:
        if (child.tag == "image"):
            img = Image(child.attrib["name"], child.attrib["name"])
            item = DatasetItem(str(ind), [], img)
            for ind, ann in enumerate(child):
                if ann.tag == 'box':
                    points = [
                              float(ann.attrib["xtl"]),
                              float(ann.attrib["ytl"]),
                              float(ann.attrib["xbr"]),
                              float(ann.attrib["ybr"]),
                              ]
                    label_id = dataset.find_label_id(ann.attrib["label"])
                    rotation = float(
                        ann.attrib["rotation"]) if "rotation" in ann.attrib else None
                    ann = Annotation(label_id, points, 'bbox', rotation)
                    item.annotations.append(ann)
                    
                elif ann.tag == 'polyline':
                    label_id = dataset.find_label_id(ann.attrib["label"])
                    points = ann.attrib['points'].replace(',', ';').split(";")

                    points = [int(round(float(p.strip())))
                              for p in points if p.strip() != '']
                    rotation = None
                    ann = Annotation(label_id, points, 'polyline', rotation)
                    item.annotations.append(ann)
                
                elif ann.tag == 'points':
                    label_id = dataset.find_label_id(ann.attrib["label"])
                    points = ann.attrib['points'].split(",")

                    points = [int(round(float(p.strip())))
                              for p in points if p.strip() != '']
                    rotation = None
                    ann = Annotation(label_id, points, 'polyline', rotation)
                    item.annotations.append(ann)

            dataset.add_item(item)

    return dataset
