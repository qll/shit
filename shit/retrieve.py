#!/usr/bin/env python2
"""Stego Helper Identification Tool - Hide"""
from scipy.misc import imread as read_img
import numpy as np
import util
import os
import json

###############################################################################
######################################################################## bit ##
###############################################################################
def decode_msg_from_bit(img_array, stegobit):
    img_bit_array = util.unpack_img_to_bits(img_array)

    bitmsg = [byte[stegobit] for byte in img_bit_array]

    msg = np.packbits(bitmsg)
    return''.join(chr(x) for x in msg if x != 0)

def decode_nth_bit(inp, stegobit):
    """Retrieves a text message in a specific colour value bit of an image"""
    assert os.path.isfile(inp), '%s is not a file.' % inp
    assert 0 <= stegobit <= 7, '%d is an invalid bit value.' %stegobit
    
    img = read_img(inp)
    res = decode_msg_from_bit(img, stegobit)
    print res
    return res

###############################################################################
################################################################## patchwork ##
###############################################################################
def decode_msg_with_patchwork(img_array, key_array_A, key_array_B):
    value = []
    for a, b in zip(key_array_A, key_array_B):
        value.append(img_array[tuple(a)] - img_array[tuple(b)])
    
    return ''.join(chr(v[0]) for v in value)

def decode_patchwork(inp, key_array_A, key_array_B):
    """Retrieves a text message which is hidden by patchwork steganography"""
    assert os.path.isfile(inp), '%s is not a file.' % inp
    img = read_img(inp)

    key_array_A = json.loads(key_array_A)
    key_array_B = json.loads(key_array_B)
    res = decode_msg_with_patchwork(img, key_array_A, key_array_B)
    print res
    return res


METHODS = {
    'bit': {
        'function': decode_nth_bit,
        'arguments': (
            {'name': 'stegobit', 'type': int, 'help': 'Bit where the message is hidden'},
            {'name': 'inp', 'metavar': 'input_path', 'help': 'Path to image'},
        )
    },
    'patchwork': {
        'function': decode_patchwork,
        'arguments': (
            {'name': 'inp', 'metavar': 'input_path', 'help': 'Path to image'},
            {'name': 'key_array_A', 'help': 'First key stream'},
            {'name': 'key_array_B', 'help': 'Second key stream'},
        )
    }
}


if __name__ == '__main__':
    util.start(__doc__, METHODS)


# path = "C:\\Users\\juckef34\\ss15\\project\\tests\\files\\diffpixels_test.png"
# b = 7
# bit(path, b)