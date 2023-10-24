import numpy as np
import json


def id2rgb(id_map):
    if isinstance(id_map, np.ndarray):
        id_map_copy = id_map.copy()
        rgb_shape = tuple(list(id_map.shape) + [3])
        rgb_map = np.zeros(rgb_shape, dtype=np.uint8)
        for i in range(3):
            rgb_map[..., i] = id_map_copy % 256
            id_map_copy //= 256
        return rgb_map
    color = []
    for _ in range(3):
        color.append(id_map % 256)
        id_map //= 256
    return color


def _create_single_category(item):
    category = {
        'id': item["id"],
        'name': item["name"],
        'supercategory': item["name"],
        'isthing': 1,
        'color': id2rgb(item["id"])
    }
    return category


def create_categories(path_to_classes):
    classes = None

    with open(path_to_classes, 'r') as fp:
        classes = json.load(fp)

    categories = [
        _create_single_category(item)
        for item in classes
    ]
    return categories
