import os
import cv2
from PIL import Image
from collections import namedtuple


def get_image_dimensions(image_path):
    img_height = None
    img_width = None

    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is not None:
        dimensions = img.shape
        img_height, img_width = (dimensions[0], dimensions[1])
    else:
        try:
            img = Image.open(image_path)
            img_width, img_height = img.size()
        except Exception as e:
            raise

    return img_height, img_width


def _sa_to_coco_single(id_, annotation_json, image_dir):
    image_commons = _prepare_single_image_commons_vector(id_, annotation_json['metadata'], image_dir)
    if image_commons is None:
        raise Exception("_prepare_single_image_commons_vector returned None")

    res = image_commons.image_info
    return res


def _prepare_single_image_commons_vector(id_, metadata, image_dir):
    ImgCommons = namedtuple('ImgCommons', ['image_info'])

    image_info = _make_image_info(
        os.path.join(image_dir, metadata['name']), metadata['height'], metadata['width'], id_
    )

    res = ImgCommons(image_info)

    return res


# def _prepare_single_image_commons(id_, metadata):
#     res = None
#     # if self.project_type == 'Pixel':
#     # res = self._prepare_single_image_commons_pixel(id_, metadata)
#     # elif self.project_type == 'Vector':
#     # res = self._prepare_single_image_commons_vector(id_, metadata)
#     res = _prepare_single_image_commons_vector(id_, metadata)
#     return res


def _make_image_info(pname, pheight, pwidth, id_):
    image_info = {
        'id': id_,
        'file_name': pname,
        'height': pheight,
        'width': pwidth,
        'license': 1
    }

    return image_info
