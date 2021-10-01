import threading
from PIL import Image
import cv2
from datetime import datetime
import json
from pathlib import Path
from collections import namedtuple
import categorySection
import imageSection
import argparse

def create_skeleton():
    out_json = {
        'info':
            {
                'url':
                    'https://mindkosh.ai',
                'version':
                    '1.0',
                'year':
                    datetime.now().year,
                'contributor':
                    'Mindkosh AI',
                'date_created':
                    datetime.now().strftime("%d/%m/%Y")
            },
        'licenses':
            [
                {
                    'url': 'https://mindkosh.com',
                    'id': 1,
                    'name': 'Mindkosh AI'
                }
            ],
        'images': [],
        'annotations': [],
        'categories': []
    }
    return out_json


def write_to_json(output_path, json_data):
    with open(output_path, 'w') as fw:
        json.dump(json_data, fw, indent=2)


def parse_json_into_common_format(sa_annotation_json, fpath):
    """
        If the annotation format ever changes this function will handle it and
        return something optimal for the converters. Additionally, if anything
        important is absent from the current json, this function fills it.
    """
    if isinstance(sa_annotation_json, list):
        # sa_annotation_json = self.convert_from_old_sa_to_new(
        #     sa_annotation_json, self.project_type
        # )
        raise Exception("Old format")

    if 'metadata' not in sa_annotation_json:
        sa_annotation_json['metadata'] = {}

    if 'tags' not in sa_annotation_json:
        sa_annotation_json['tags'] = []

    if 'instances' not in sa_annotation_json:
        sa_annotation_json['instances'] = []

    if 'comments' not in sa_annotation_json:
        sa_annotation_json['comments'] = []

    if 'name' not in sa_annotation_json[
            'metadata'] or sa_annotation_json['metadata']['name'] is None:
        fname = fpath.name

        sa_annotation_json['metadata']['name'] = fname

    sa_annotation_json['metadata']['image_path'] = str(
        Path(fpath).parent / "images" / sa_annotation_json['metadata']['name']
    )

    sa_annotation_json['metadata']['annotation_json'] = fpath

    # if self.task == 'panoptic_segmentation':
    #     panoptic_mask = str(
    #         Path(self.export_root) /
    #         (sa_annotation_json['metadata']['name'] + '.png')
    #     )

    #     sa_annotation_json['metadata']['panoptic_mask'] = panoptic_mask

    # if self.project_type == 'Pixel':
    #     sa_annotation_json['metadata']['sa_bluemask_path'] = str(
    #         Path(self.export_root) /
    #         (sa_annotation_json['metadata']['name'] + '___save.png')
    #     )

    if not isinstance(
        sa_annotation_json['metadata'].get('height', None), int
    ) or not isinstance(
        sa_annotation_json['metadata'].get('width', None), int
    ):
        image_height, image_width = imageSection.get_image_dimensions(
            sa_annotation_json['metadata']['image_path']
        )
        sa_annotation_json['metadata']['height'] = image_height
        sa_annotation_json['metadata']['width'] = image_width

    return sa_annotation_json


def make_annotation(
    category_id, image_id, bbox, segmentation, area, anno_id
):
    # if self.task == 'object_detection':
    #     segmentation = [
    #         [
    #             bbox[0], bbox[1], bbox[0], bbox[1] + bbox[3],
    #             bbox[0] + bbox[2], bbox[1] + bbox[3], bbox[0] + bbox[2],
    #             bbox[1]
    #         ]
    #     ]
    annotation = {
        'id': anno_id,  # making sure ids are unique
        'image_id': image_id,
        # 'segmentation': segmentation,
        'iscrowd': 0,
        'bbox': bbox,
        'area': area,
        'category_id': category_id
    }

    return annotation


def make_id_generator():
    cur_id = 0
    while True:
        cur_id += 1
        yield cur_id


def sa_vector_to_coco_object_detection(instances, annot_id_generator, idx):
    annotations_per_image = []

    for instance in instances:
        if instance['type'] != 'bbox':
            print(
                "Skipping '%s' type convertion during object_detection task",
                instance['type']
            )
            return []

        anno_id = next(annot_id_generator)
        category_id = instance['classId']
        points = instance['points']
        for key in points:
            points[key] = round(points[key], 2)
        bbox = (
            points['x1'], points['y1'], points['x2'] - points['x1'],
            points['y2'] - points['y1']
        )
        polygons = bbox
        area = int((points['x2'] - points['x1']) * points['y2'] - points['y1'])

        annotation = make_annotation(
            category_id, idx, bbox, polygons, area, anno_id
        )
        annotations_per_image.append(annotation)
    return annotations_per_image


def convert_sa_to_coco_and_save( fpath, class_path, outpath ):
    all_annotations = {}

    out_json = create_skeleton()
    out_json['categories'] = categorySection.create_categories(class_path)

    images = []
    annotations = []

    image_id_generator = make_id_generator()
    annot_id_generator = make_id_generator()

    image_dir = str( Path(fpath).parent / "images" )
    with open(fpath, 'r') as fp:
        json_data = json.load(fp)

    for i in json_data.keys():
        if i == "___sa_version___":
            continue
        else:
            ann = parse_json_into_common_format(json_data[i], fpath)

            # idx = next(annot_id_generator)
            image_idx = next(image_id_generator)
            res = imageSection._sa_to_coco_single(image_idx, ann, image_dir)
            images.append(res)

            fin_ann = sa_vector_to_coco_object_detection(
                ann["instances"], annot_id_generator, res["id"])

            annotations.extend(fin_ann)

    out_json['annotations'] = annotations
    out_json['images'] = images
    write_to_json(
        outpath, out_json
    )


if __name__ == '__main__':
    # default_fpath = "/home/sdevgupta/superannotate_projects/ert/annotations.json"
    # default_class_path = "/home/sdevgupta/superannotate_projects/ert/classes.json"
    # default_outpath = "/home/sdevgupta/superannotate_projects/export/annotations_coco.json"
    
    parser = argparse.ArgumentParser( description='Convert Superannotate labels to COCO format' )
    parser.add_argument(action='store', dest='fpath')
    parser.add_argument(action='store', dest='class_path')
    parser.add_argument(action='store', dest='outpath')
    args = parser.parse_args()
    
    fpath = args.fpath
    class_path = args.class_path
    outpath = args.outpath

    convert_sa_to_coco_and_save(fpath, class_path, outpath)
