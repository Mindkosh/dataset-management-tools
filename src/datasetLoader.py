import os
import utils
from datumaro.components.dataset import Dataset
import cvat_format

class DatasetLoader:
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
    
    def get_annotations(self):
        return self.annotations