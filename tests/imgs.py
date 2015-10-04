"""Unit test helper: Offer images with different image modes.""" 
import numpy as np
import os
import random
import scipy.misc
import string
import tempfile
from PIL import Image


class TempFile:
    def __init__(self, img=None):
        self.path = self.create_unique_name('.png')
        if isinstance(img, Image.Image):
            img.save(self.path, format='png')
        elif isinstance(img, np.ndarray):
            scipy.misc.imsave(self.path, img)
        elif img is not None:
            raise Exception('Unknown format for img: %s' % img.__class__)

    def create_unique_name(self, suffix):
        name = 'tmp' + ''.join(random.choice(string.letters) for _ in range(8))
        while os.path.isfile('%s%s' % (name, suffix)):
            name += random.choice(string.letters)
        return '%s%s' % (name, suffix)

    def __enter__(self):
        return self.path

    def __exit__(self, type, value, traceback):
        if os.path.isfile(self.path):
            os.remove(self.path)



def _create_img(mode, size, color):
    img = Image.new(mode=mode, size=size, color=color)
    img.color = color  # a bit of monkey patching in unit tests :-)
    return img


def create_rgb(size=(100, 100), color=(0, 0, 0)):
    return _create_img('RGB', size, color)


def create_gray(size=(100, 100), color=0):
    return _create_img('L', size, color)


def get_imgs():
    """Build multiple images with differing image modes."""
    # https://pillow.readthedocs.org/handbook/concepts.html#concept-modes
    modes = (
        # 3x8-bit pixels, true color
        ('RGB', (255, 255, 255)),
        # 4x8-bit pixels, true color with transparency mask
        ('RGBA', (255, 255, 255, 255)),
        # 8-bit pixels, black and white
        ('L', 255),
        # 1-bit pixels, black and white, stored with one pixel per byte
        ('1', 255),
    )
    size = (100, 100)
    imgs = []
    for mode, color in modes:
        img = Image.new(mode, size, color)
        img.color = color  # a bit of monkey patching should be ok in uts :-)
        imgs.append(img)
    return imgs


def sub_from_color(color, value):
    """Subtract value from a color."""
    sub = lambda v: (v - value) % 256
    if isinstance(color, int):
        return sub(color)
    return tuple(map(sub, color))


def sub_colors(color1, color2):
    """Subtract two colors from each other."""
    sub = lambda a, b: (a - b) % 256
    if isinstance(color1, int) and isinstance(color2, int):
        return sub(color1, color2)
    return tuple(sub(a, b) for a, b in zip(color1, color2))


def wrap(value):
    if isinstance(value, list) or isinstance(value, tuple):
        return value
    return [value]
