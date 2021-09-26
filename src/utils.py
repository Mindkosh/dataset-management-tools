import os
from pathlib import Path

def get_assets_dir():
    path = Path(os.path.dirname(os.path.realpath(__file__)))
    parent_dir = path.parent.absolute()
    assets_dir = os.path.join( parent_dir, "assets" )
    return assets_dir