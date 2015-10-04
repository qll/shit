#!/usr/bin/env python2
import numpy as np
import os
import scipy.misc
import sys
import unittest


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, '..', 'shit'))
import analyse
import hide
import retrieve


class IntegrationTest(unittest.TestCase):
    def test_encode_decode_msg_from_bit(self):
        IMG = scipy.misc.lena()
        MSG = 'This test works well'
        # test with lsb
        stego_img = hide.encode_msg_in_bit(img_array=IMG, msg=MSG, stegobit=7)
        msg = retrieve.decode_msg_from_bit(img_array=stego_img, stegobit=7)
        self.assertEqual(MSG, msg)
        # test with bit in between
        stego_img = hide.encode_msg_in_bit(img_array=IMG, msg=MSG, stegobit=4)
        msg = retrieve.decode_msg_from_bit(img_array=stego_img, stegobit=4)
        self.assertEqual(MSG, msg)
        # test with msb
        stego_img = hide.encode_msg_in_bit(img_array=IMG, msg=MSG, stegobit=0)
        msg = retrieve.decode_msg_from_bit(img_array=stego_img, stegobit=0)
        self.assertEqual(MSG, msg)

    def test_constructed_strings(self):
        IMG = scipy.misc.lena()
        MSG1 = 'Steganography has no chance'
        MSG2 = 'Really really no chance'
        # first, hide two messages in the same image
        stego_img = hide.encode_msg_in_bit(img_array=IMG, msg=MSG1, stegobit=7)
        stego_img = hide.encode_msg_in_bit(img_array=stego_img, msg=MSG2,
                                           stegobit=5)
        # then, check if we get it back out
        msgs1 = analyse.constructed_strings(img_array=stego_img, threshold=4)
        msgs1 = list(msgs1)
        self.assertIn(MSG1, msgs1)
        self.assertIn(MSG2, msgs1)
        # test with a higher threshold (fewer garbage strings)
        msgs2 = analyse.constructed_strings(img_array=stego_img, threshold=14)
        msgs2 = list(msgs2)
        self.assertIn(MSG1, msgs2)
        self.assertIn(MSG2, msgs2)
        # we should get a lot fewer results for a higher threshold
        self.assertTrue(len(msgs1) > len(msgs2))


if __name__ == '__main__':
    unittest.main()
