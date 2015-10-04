#!/usr/bin/env python2
"""Stego Helper Identification Tool - Analyser"""
import log
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy.misc 
import string
import sys
import util
from PIL import Image


###############################################################################
########################################################### helper functions ##
###############################################################################
def open_img(img_path_or_obj):
    """Ensure img_path_or_obj is a Pillow Image object."""
    if isinstance(img_path_or_obj, Image.Image):
        img = img_path_or_obj
    else:
        assert os.path.isfile(img_path_or_obj), ('%s is not a file'
                                                 % img_path_or_obj)
        img = Image.open(img_path_or_obj)
    log.debug('%s is in %s mode', img_path_or_obj, img.mode)
    return img


def open_img_array(img_path_or_array):
    """Ensure img_path_or_array is a numpy array."""
    if isinstance(img_path_or_array, np.ndarray):
        return img_path_or_array
    assert os.path.isfile(img_path_or_array), ('%s is not a file'
                                               % img_path_or_array)
    return scipy.misc.imread(img_path_or_array)


def save_img(img, out_path):
    if out_path is not None:
        log.info('Saving output image to %s', out_path)
        img.save(out_path)


def save_img_array(img_array, out_path):
    if out_path is not None:
        log.info('Saving output image at %s', out_path)
        scipy.misc.imsave(out_path, img_array)


def build_base_path(out_path, img_path):
    """Build base path for bulk data writes."""
    assert os.path.isdir(out_path), '%s is not a directory' % out_path
    return os.path.join(out_path, os.path.basename(img_path)) + '_'


def match_imgs(img1_path, img2_path):
    """Match images together and check properties like mode and dimension."""
    img1 = open_img(img1_path)
    img2 = open_img(img2_path)
    if img1.mode != img2.mode:
        log.warning('Unequal image modes (%s vs %s) - converting %s to %s',
                    img1.mode, img2.mode, img1.mode, img2.mode)
        img1 = img1.convert(img2.mode)
    if img1.width != img2.width or img1.height != img2.height:
        log.warning('Dimensions do not match ([%d, %d] vs [%d, %d])',
                    img1.width, img1.height, img2.width, img2.height)
    return img1, img2


def iter_planes(img):
    """Generator over all bit planes in all bands of a Pillow Image object."""
    bands = img.getbands()
    band_list = list(enumerate(bands))
    if len(bands) > 1:  # if there is only one band, None and 0 are the same
        band_list += [(None, ''.join(bands))]
    for band_index, band in band_list:
        data = np.array(list(img.getdata(band=band_index)), dtype=np.uint8)
        for plane_bit, plane in ((i, data >> i & 1) for i in range(8)):
            yield band, plane_bit, plane


###############################################################################
####################################################################### auto ##
###############################################################################
def has_duplicates_in_palette(palette):
    """Check for duplicate color values in an image color palette."""
    if palette is None:
        return False
    assert len(palette) % 3 == 0, 'Color palette not divisible by three'
    palette = np.array(palette).reshape((len(palette) / 3, 3))
    for i in range(len(palette)):
        if palette[i] in palette[:i]:  # memoization would be faster
            return True
    return False


def analyse(img_path):
    """Search for best steganalysis method and recommend it to me."""
    img = open_img(img_path)
    if has_duplicates_in_palette(img.getpalette()):
        log.info('Found duplicate values in color palette - this might be '
                 'used to hide messages in an image')
        log.info('Execute: %s palette %s OUTPUT_PATH.png',
                 sys.argv[0], img_path)


###############################################################################
#################################################################### combine ##
###############################################################################
def combine(expression, img1_path, img2_path, out_path=None):
    """Combine two images based on a user defined expression."""
    def reshape_to(src, dest):
        size = dest.size - src.size
        return np.append(src.ravel(), np.zeros((size,))).reshape(dest.shape)
    img1 = open_img_array(img1_path)
    img2 = open_img_array(img2_path)
    if img1.size < img2.size:
        img1 = reshape_to(img1, img2)
    elif img2.size < img1.size:
        img2 = reshape_to(img2, img1)
    result = eval(expression)
    save_img_array(result, out_path)
    return result


###############################################################################
####################################################################### diff ##
###############################################################################
def diffed_imgs(img1, img2):
    """Generator over all Pillow Image object pixel differences.

    Will run in the boundaries of min{width, height} of both images. It is the
    caller's responsibility to match image modes (RGB <-> RGBA).
    """
    for y in range(min(img1.height, img2.height)):
        for x in range(min(img1.width, img2.width)):
            img1_pixel = img1.getpixel((x, y))
            img2_pixel = img2.getpixel((x, y))
            if img1_pixel != img2_pixel:
                yield (x, y), img1_pixel, img2_pixel


def find_diffs(orig_path, stego_path, out_path=None):
    """Find differences in pixel values of the original and stego image."""
    orig, stego = match_imgs(orig_path, stego_path)
    out = Image.new('RGB', orig.size, (0, 0, 0)) if out_path else None
    for pos, orig_pixel, stego_pixel in diffed_imgs(orig, stego):
        log.info('Mismatched pixels at %s: %s vs %s', pos, orig_pixel,
                 stego_pixel)
        if out:
            out.putpixel(pos, (255, 0, 0))
    if out:
        out.save(out_path)


###############################################################################
####################################################################### draw ##
###############################################################################
def draw(img_path, out_path):
    """Run Xth bit stego on all planes and interpret the results as images."""
    base_path = build_base_path(out_path, img_path)
    img = open_img(img_path)
    img_size = np.prod(img.size)
    for band, plane_bit, plane in iter_planes(img):
        plane *= 255  # lift 1 up to 255 (white) and keep 0 at 0 (black)
        if plane.size != img_size:
            plane = np.average(plane, axis=1)
        draw_img = Image.new(mode='L', size=img.size)
        draw_img.putdata(plane)
        save_img(draw_img, '%s%s_plane_%d.png' % (base_path, band, plane_bit))


###############################################################################
#################################################################### extract ##
###############################################################################
def extract(img_path, out_path):
    """Run Xth bit stego on all planes and extract the raw data."""
    img = open_img(img_path)
    base_path = build_base_path(out_path, img_path)
    for band, plane_bit, plane in iter_planes(img):
        data = np.packbits(plane.ravel())
        file_name = '%s%s_plane_%d' % (base_path, band, plane_bit)
        with open(file_name, 'wb') as fp:
            log.info('Saving output data to %s' % file_name)
            fp.write(data.tobytes())


###############################################################################
################################################################## histogram ##
###############################################################################
def generate_histogram(img_path, out_path):
    """Draw a color value histogram."""
    img = open_img(img_path)
    plt.xlabel('color value')
    plt.ylabel('# of values')
    frame = plt.gca()
    for i, band in enumerate(img.getbands()):
        plt.hist(img.getdata(band=i), bins=256, color=band.lower(), alpha=0.3)
    plt.savefig(out_path)


###############################################################################
##################################################################### modify ##
###############################################################################
def modify(expression, img_path, out_path=None):
    """Modify each pixel value of the image with a user defined expression."""
    log.info('Executing expression "%s" on each pixel value', expression)
    img = Image.eval(open_img(img_path), lambda value: eval(expression))
    save_img(img, out_path)
    return img


###############################################################################
#################################################################### palette ##
###############################################################################
def fix_palette(img_path, out_path=None):
    """Change whole color palette to grayscale uncovering duplicate entries."""
    img = open_img(img_path)
    assert img.getpalette() is not None, 'This image has no color palette'
    img.putpalette(np.array([(i, i, i) for i in range(256)]).ravel())
    save_img(img, out_path)
    return img


###############################################################################
#################################################################### strings ##
###############################################################################
def iter_strings(plane, threshold):
    """Generator over all strings in a bit plane."""
    printables = []
    for char in np.packbits(plane.ravel()).tostring():
        if char in string.printable:
            printables.append(char)
        else:
            if len(printables) >= threshold:
                yield ''.join(printables)
            printables = []
    if len(printables) >= threshold:
        yield ''.join(printables)


def find_strings(img_path, threshold=4):
    """Display all printable strings of LSB, MSB and Xth Bit stego."""
    assert threshold > 0, 'Threshold cannot be smaller than or equal to 0'
    img = open_img(img_path)
    for band, plane_bit, plane in iter_planes(img):
        log.debug('Outputting plane %d of band %d', plane_bit, band)
        for string in iter_strings(plane, threshold):
            log.info(string)


###############################################################################
######################################################### command line stuff ##
###############################################################################
METHODS = {
    'auto': {
        'function': analyse,
        'arguments': (
            {'name': 'img_path', 'metavar': 'IMAGE_PATH',
             'help': 'Path to suspected stego image'},
        )
    },
    'combine': {
        'function': combine,
        'arguments': (
            {'name': 'expression', 'metavar': 'EXPRESSION',
             'help': 'Python expression like "img1 - img2"'},
            {'name': 'img1_path', 'metavar': 'IMG1_PATH',
             'help': 'First image path'},
            {'name': 'img2_path', 'metavar': 'IMG2_PATH',
             'help': 'Second image path'},
            {'name': 'out_path', 'metavar': 'OUT_PATH',
             'help': 'Resulting image path'},
        )
    },
    'diff': {
        'function': find_diffs,
        'arguments': (
            {'name': 'orig_path', 'metavar': 'ORIG', 'help': 'Original image'},
            {'name': 'stego_path', 'metavar': 'STEGO', 'help': 'Stego image'},
            {'flags': ('-o', '--output'), 'dest': 'out_path',
             'help': 'Output image where differences are marked by red pixels'}
        )
    },
    'draw': {
        'function': draw,
        'arguments': (
            {'name': 'img_path', 'metavar': 'IMG_PATH', 'help': 'Image path'},
            {'name': 'out_path', 'metavar': 'OUT_PATH',
             'help': 'Directory where the resulting images will be stored'},
        )
    },
    'extract': {
        'function': extract,
        'arguments': (
            {'name': 'img_path', 'metavar': 'IMG_PATH', 'help': 'Image path'},
            {'name': 'out_path', 'metavar': 'OUT_PATH',
             'help': 'Directory where the resulting images will be stored'},
        )
    },
    'histogram': {
        'function': generate_histogram,
        'arguments': (
            {'name': 'img_path', 'metavar': 'IMG_PATH', 'help': 'Image path'},
            {'name': 'out_path', 'metavar': 'OUT_HIST_PATH',
             'help': 'Histogram path'},
        )
    },
    'modify': {
        'function': modify,
        'arguments': (
            {'name': 'expression', 'metavar': 'EXPRESSION',
             'help': 'Python expression, like "value ^ 177"'},
            {'name': 'img_path', 'metavar': 'IMAGE_PATH',
             'help': 'Input image path'},
            {'name': 'out_path', 'metavar': 'OUTPUT_PATH',
             'help': 'Output image path'},
        )
    },
    'palette': {
        'function': fix_palette,
        'arguments': (
            {'name': 'img_path', 'metavar': 'IMAGE_PATH',
             'help': 'Path to suspected steganographic image'},
            {'name': 'out_path', 'metavar': 'OUTPUT_PATH',
             'help': 'File output path with changed color palette'},
        )
    },
    'strings': {
        'function': find_strings,
        'arguments': (
            {'name': 'img_path', 'metavar': 'IMAGE_PATH',
             'help': 'Path to suspected steganographic image'},
            {'flags': ('-t', '--threshold'), 'type': int, 'default': 4,
             'help': 'Print any sequence of at least X printables'},
        )
    },
}


if __name__ == '__main__':
    util.start(__doc__, METHODS)
