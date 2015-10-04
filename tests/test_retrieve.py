#!/usr/bin/env python2
import os
import sys
import unittest
import numpy as np
from scipy.misc import lena


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, '..', 'shit'))
import retrieve


class RetrieveTest(unittest.TestCase):
	###########################################################################
    #################################################################### bit ##
    ###########################################################################
    def test_img_path_is_not_a_file(self):
        with self.assertRaises(AssertionError):
            retrieve.decode_nth_bit(inp="./nonExistent", stegobit=3)

    def test_wrong_stegobit_value(self):
        with self.assertRaises(AssertionError):
            retrieve.decode_nth_bit(inp=__file__, stegobit=9)
            
        with self.assertRaises(AssertionError):
            retrieve.decode_nth_bit(inp=__file__, stegobit=-1)

    ###########################################################################
    ############################################################## patchwork ##
    ###########################################################################
    def test_img_path_is_not_a_file(self):
        with self.assertRaises(AssertionError):
            retrieve.decode_patchwork(inp="./nonExistent", key_array_A=[(23, 12), (12, 23)], key_array_B=[(34, 52), (52, 34)])

if __name__ == '__main__':
    unittest.main()