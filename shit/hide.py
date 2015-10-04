#!/usr/bin/env python2
"""Stego Helper Identification Tool - Hide"""
from scipy.misc import imread as read_img
from scipy.misc import imsave as save_image
import numpy as np
import util
import os
import random
import json

################################################################################
######################################################################### bit ##
################################################################################
def write_img(path, img_array):
    image = img_array.reshape(img_array.shape)
    save_image(path, image)


def convert_msg_to_bin(msg):
    letterlist = np.array([ord(m) for m in msg])
    binarray = np.array([bin(l)[2:].zfill(8) for l in letterlist]) 
    res = "".join(binarray)

    return map(int, res)


def encode_msg_in_bit(img_array, msg, stegobit):
    assert len(msg) * 8 < img_array.size, 'The message is too long for this image.'

    binmsg = np.array(convert_msg_to_bin(msg), dtype= np.uint8)
    zeros = np.zeros(img_array.size - binmsg.size, dtype=np.uint8)
    padmsg = np.append(binmsg, zeros)

    img_bit_array = util.unpack_img_to_bits(img_array.astype(np.uint8))

    #manipulation
    for byte, msg_bit in zip(img_bit_array, padmsg): 
        byte[stegobit] = msg_bit

    return util.pack_bits_to_img(img_bit_array, img_array)


def encode_nth_bit(inp, out, msg, stegobit):
    """Hides a text message in one bit of each colour value of an image."""
    assert os.path.isfile(inp), '%s is not a file.' % inp
    assert 0 <= stegobit <= 7, '%d is an invalid bit value.' %stegobit
    img = read_img(inp)

    #while writing an jpg image, compression destroys the steganographic message
    ext = os.path.splitext(out)[1].lower()
    assert ext != '.jpeg' and ext != '.jpg', 'jpg/jpeg is currently not a valid extension for output images.'
    write_img(out, encode_msg_in_bit(img, msg, stegobit))


################################################################################
################################################################### patchwork ##
################################################################################
def get_random_pos(length, img_array, array_A=[]):
    pos = []
    while len(pos) < length:
        x = random.randint(0, img_array.shape[0] - 1)
        y = random.randint(0, img_array.shape[1] - 1)
        if (x, y) not in pos and (x, y) not in array_A:
            pos.append((x, y))
    return pos


def encode_msg_with_patchwork(img_array, msg, key_array_A, key_array_B):
    int_msg = [ord(c) for c in msg]

    for i, c in enumerate(int_msg):
        img_array[key_array_B[i]] = img_array[key_array_A[i]]
        img_array[key_array_A[i]] = img_array[key_array_A[i]] + c

    return img_array


def encode_patchwork(inp, out, msg):
    """Hides a text message in pixels of two key streams."""
    assert os.path.isfile(inp), '%s is not a file.' % inp
    img = read_img(inp)
    
    A = get_random_pos(len(msg), img)
    B = get_random_pos(len(msg), img, A)
    print "A: %s" %json.dumps(A)
    print "B: %s" %json.dumps(B)

    #while writing an jpg image, compression destroys the steganographic message
    ext = os.path.splitext(out)[1].lower()
    assert ext != '.jpeg' and ext != '.jpg', 'jpg/jpeg is currently not a valid extension for output images.'
    save_image(out, encode_msg_with_patchwork(img, msg, A, B))


METHODS = {
    'bit': {
        'function': encode_nth_bit, 
        'arguments': (
            {'name': 'stegobit','type': int, 'help': 'Bit where the message becomes hidden'},
            {'name': 'inp', 'metavar': 'input_path', 'help': 'Path to input image'}, 
            {'name': 'out', 'metavar': 'output_path', 'help': 'Path to output image'}, 
            {'name': 'msg', 'metavar': 'message', 'help': 'Message to hide in image'},  
        )
    },
    'patchwork': {
        'function': encode_patchwork,
        'arguments': (
            {'name': 'inp', 'metavar': 'input_path', 'help': 'Path to input image'}, 
            {'name': 'out', 'metavar': 'output_path', 'help': 'Path to output image'}, 
            {'name': 'msg', 'metavar': 'message', 'help': 'Message to hide in image'})
    }
}


if __name__ == '__main__':
    util.start(__doc__, METHODS)

# path = "C:\\Users\\juckef34\\ss15\\project\\tests\\files\\diffpixels.png"
# path2 = "C:\\Users\\juckef34\\ss15\\project\\tests\\files\\diffpixels_test.png"
# msg = "Nico ist toll"
# stegobit = 7

# bit(path, path2, msg, stegobit)
