#!/usr/bin/env python2
"""Stego Helper Identification Tool - Analyser"""
import logging as log
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as pltimg
import os
import util
from PIL import Image


# def _draw_histogram(name, mode, histogram, output_file):
#     plt.title('Histogram of %s' % name)
#     plt.xlabel('color value (%s)' % mode)
#     plt.ylabel('# of values')
#     plt.hist(histogram, len(histogram))
#     plt.savefig(output_file)


# def histogram(input, output=None):
#     img = Image.open(input)
#     histogram = img.histogram()
#     input_name = os.path.basename(input)
#     if output is None:
#         output = input_name + '_hist.png'
#     _draw_histogram(input_name, img.mode, histogram, output)
#     _log.info('Saved histogram to %s' % output)


def diffpixels(orig_file, stego_file):
    assert os.path.isfile(orig_file), '%s is not a file.' % orig_file
    assert os.path.isfile(stego_file), '%s is not a file.' % stego_file

    orig = Image.open(orig_file)
    stego = Image.open(stego_file)
    if orig.mode != stego.mode:
        log.warning('Unequal image modes (%s vs %s). Trying to convert '
                    'original image to %s.', orig.mode, stego.mode, stego.mode)
        orig = orig.convert(stego.mode)
    if orig.width != stego.width or orig.height != stego.height:
        log.warning('Dimensions do not match ([%d, %d] vs [%d, %d]).',
                    orig.width, orig.height, stego.width, stego.height)
    # TODO(nicolas): enhance performance (scipy.imread is faster but does not
    #                seem to have a way to convert image modes [RGB, ...])
    for y in range(min(orig.height, stego.height)):
        for x in range(min(orig.width, stego.width)):
            orig_pixel = orig.getpixel((x, y))
            stego_pixel = stego.getpixel((x, y))
            if orig_pixel != stego_pixel:
                log.info('Mismatched pixels at (%d, %d): %s vs %s',
                         x, y, orig_pixel, stego_pixel)


METHODS = {
    'diffpixels': {
        'help': 'Diff pixels of original and stego image',
        'arguments': (
            {'name': 'orig_file', 'metavar': 'ORIG', 'help': 'Original image'},
            {'name': 'stego_file', 'metavar': 'STEGO', 'help': 'Stego image'},
        )
    }
}


if __name__ == '__main__':
    util.start(__doc__, METHODS, globals())
