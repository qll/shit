#!/usr/bin/env python2
import os
import sys
import unittest
import numpy as np
from scipy.misc import lena


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, '..', 'shit'))
import hide


class HideTest(unittest.TestCase):
    ###########################################################################
    #################################################################### bit ##
    ###########################################################################
    def test_convert_msg_to_bin(self):
        MSG = "OK"
        BINMSG = [0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1]

        self.assertEqual(BINMSG, hide.convert_msg_to_bin(MSG))

    def test_msg_too_long_for_image(self):
        with self.assertRaises(AssertionError):
            hide.encode_msg_in_bit(img_array=lena(), msg="A" * (lena().size + 1), stegobit=3)

    def test_img_path_is_not_a_file(self):
        with self.assertRaises(AssertionError):
            hide.encode_nth_bit(inp="./nonExistent", out="./", msg="OK", stegobit=3)

    def test_wrong_stegobit_value(self):
        with self.assertRaises(AssertionError):
            hide.encode_nth_bit(inp=__file__, out="./", msg="OK", stegobit=9)
        with self.assertRaises(AssertionError):
            hide.encode_nth_bit(inp=__file__, out="./", msg="OK", stegobit=-1)

    def test_if_output_extension_equals_jpg(self):
        for test in ('jpg', 'jpeg', 'jpEg', 'JPG'):
            with self.assertRaises(AssertionError):
                hide.encode_nth_bit(inp=__file__, out="./bla.%s" % test, msg="OK", stegobit=1)

    ###########################################################################
    ############################################################## patchwork ##
    ###########################################################################
    def test_img_path_is_not_a_file(self):
        with self.assertRaises(AssertionError):
            hide.encode_patchwork(inp="./nonExistent", out="./", msg="OK")

    def test_if_output_extension_equals_jpg(self):
        for test in ('jpg', 'jpeg', 'jpEg', 'JPG'):
            with self.assertRaises(AssertionError):
                hide.encode_patchwork(inp=__file__, out="./bla.%s" % test, msg="OK")

if __name__ == '__main__':
    unittest.main()
