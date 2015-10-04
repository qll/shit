#!/usr/bin/env python2
import imgs
import numpy as np
import os
import random
import scipy.misc
import sys
import unittest
from PIL import Image


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, '..', 'shit'))
import analyse
import log


log.disable()


class AnalyseTest(unittest.TestCase):
    ###########################################################################
    ####################################################### helper functions ##
    ###########################################################################
    def test_open_img(self):
        img = imgs.create_rgb()
        # given an Pillow Image, open_img should return the same instance
        self.assertEqual(id(img), id(analyse.open_img(img)))
        # given an path, open_img should return a Pillow Image instance
        with imgs.TempFile(img) as img_path:
            opened_img = analyse.open_img(img_path)
            self.assertTrue(isinstance(opened_img, Image.Image))
            self.assertEqual(list(img.getdata()), list(opened_img.getdata()))

    def test_open_img_nonexistent(self):
        with self.assertRaisesRegexp(AssertionError, 'not a file'):
            analyse.open_img('nonexistent')

    def test_open_img_array(self):
        img_array = scipy.misc.lena()
        # given an numpy.ndarray, open_img_array should return the same inst
        self.assertEqual(id(img_array), id(analyse.open_img_array(img_array)))
        # given an path, open_img_array should return an numpy.ndarray
        with imgs.TempFile(img_array) as img_path:
            opened_array = analyse.open_img_array(img_path)
            self.assertTrue(isinstance(opened_array, np.ndarray))

    def test_open_img_array_nonexistent(self):
        with self.assertRaisesRegexp(AssertionError, 'not a file'):
            analyse.open_img_array('nonexistent')

    def test_save_img(self):
        img = imgs.create_rgb()
        # when out_path is None, this should not write any file
        with imgs.TempFile() as path:
            analyse.save_img(img, None)
            self.assertFalse(os.path.isfile(path))
        # when out_path is set to a string, save_img should save the file
        with imgs.TempFile() as path:
            analyse.save_img(img, path)
            self.assertTrue(os.path.isfile(path))

    def test_save_img_array(self):
        img_array = scipy.misc.lena()
        # when out_path is None, save_img_array should not write any file
        with imgs.TempFile() as path:
            analyse.save_img_array(img_array, None)
            self.assertFalse(os.path.isfile(path))
        # when out_path is set to a string, save_img_array should save the file
        with imgs.TempFile() as path:
            analyse.save_img_array(img_array, path)
            self.assertTrue(os.path.isfile(path))

    def test_match_imgs(self):
        """Test if the automatic conversion between modes works as intended."""
        images = imgs.get_imgs()
        for img in images:
            with imgs.TempFile(img) as img1_path:
                with imgs.TempFile(images[0]) as img2_path:
                    img1, img2 = analyse.match_imgs(img1_path, img2_path)
                    self.assertEqual(img1.mode, img2.mode)

    def test_iter_planes(self):
        img = imgs.create_rgb()
        planes = list(analyse.iter_planes(img))
        # 3 bands (R, G, B) w/ 8 planes + 1 special band (RGB) with 8 planes
        self.assertEqual(3 * 8 + 8, len(planes))
        band, bit, plane = planes[0]
        self.assertEqual('R', band)
        self.assertEqual(0, bit)
        self.assertEqual(np.prod(img.size), plane.size)
        self.assertEqual(0, plane.sum())

    def test_iter_planes_grayscale(self):
        img = imgs.create_gray()
        planes = list(analyse.iter_planes(img))
        self.assertEqual(8, len(planes))  # one band with 8 planes
        band, bit, plane = planes[0]
        self.assertEqual(0, bit)
        self.assertEqual(np.prod(img.size), plane.size)
        self.assertEqual(0, plane.sum())

    ###########################################################################
    ################################################################### auto ##
    ###########################################################################
    def test_has_duplicates_in_palette(self):
        duplicate_img = self.create_palette_img()
        duplicate_img.putpalette(0 for _ in range(256 * 3))
        duplicate_palette = duplicate_img.getpalette()
        self.assertTrue(analyse.has_duplicates_in_palette(duplicate_palette))
        fixed_palette = analyse.fix_palette(duplicate_img).getpalette()
        self.assertFalse(analyse.has_duplicates_in_palette(fixed_palette))

    ###########################################################################
    ################################################################ combine ##
    ###########################################################################
    def test_combine(self):
        img1_array = scipy.misc.lena()
        img2_array = scipy.misc.lena()
        sub_result = analyse.combine('img1 - img2', img1_array, img2_array)
        self.assertEqual(0, sub_result.sum())
        add_result = analyse.combine('img1 + img2', img1_array, img2_array)
        add_testval = img1_array.ravel()[0] + img2_array.ravel()[0]
        self.assertEqual(add_testval, add_result.ravel()[0])

    def test_combine_unequal_dimensions(self):
        """Check if smaller image is casted to bigger one."""
        img1_array = scipy.misc.lena()

        smaller_array = np.ones(shape=(100, 100, 3), dtype=np.uint8)  # rgb img
        result = analyse.combine('img1 - img2', img1_array, smaller_array)
        self.assertEqual(result.shape, img1_array.shape)
        bigger_array = np.ones(shape=(1000, 100, 3), dtype=np.uint8)  # rgb img
        result = analyse.combine('img1 - img2', img1_array, bigger_array)
        self.assertEqual(result.shape, bigger_array.shape)

        testval = img1_array.ravel()[0] - 1
        self.assertEqual(testval, result.ravel()[0])

    def test_combine_output(self):
        img1_array = scipy.misc.lena()
        img2_array = scipy.misc.lena()
        with imgs.TempFile() as tmp_path:
            analyse.combine('img1 ^ img2', img1_array, img2_array, tmp_path)
            self.assertTrue(os.path.isfile(tmp_path))

    ###########################################################################
    ################################################################### diff ##
    ###########################################################################
    def test_diffed_imgs(self):
        """Introduce one difference and check if it gets detected."""
        DIFF_POS = (50, 50)
        for img in imgs.get_imgs():
            diff_color = imgs.sub_from_color(img.color, 20)
            diff_img = img.copy()
            diff_img.putpixel(DIFF_POS, diff_color)
            differences = list(analyse.diffed_imgs(img, diff_img))
            self.assertEqual(1, len(differences))
            pos, img_pixel, diff_img_pixel = differences[0]
            self.assertEqual(DIFF_POS, pos)
            self.assertEqual(diff_color, diff_img_pixel)
            self.assertEqual(img.color, img_pixel)

    def test_diffed_imgs_equal_imgs(self):
        """Don't yield a difference on two equal images."""
        for img in imgs.get_imgs():
            differences = list(analyse.diffed_imgs(img, img.copy()))
            self.assertEqual(0, len(differences))

    def test_diffed_imgs_unequal_bounds(self):
        """Do not detect changes outside comparison bounds."""
        for img in imgs.get_imgs():
            diff_img = img.crop(box=(0, 0, 50, 50))
            diff_color = imgs.sub_from_color(img.color, 20)
            img.putpixel(xy=(60, 60), value=diff_color)
            differences = list(analyse.diffed_imgs(img, diff_img))
            self.assertEqual(0, len(differences))

    def test_find_diffs(self):
        DIFF_POS = (20, 20)
        for img in imgs.get_imgs():
            diff_color = imgs.sub_from_color(img.color, 12)
            diff_img = img.copy()
            diff_img.putpixel(DIFF_POS, diff_color)
            with imgs.TempFile() as path:
                analyse.find_diffs(img, diff_img, out_path=path)
                out_img = Image.open(path)
                self.assertEqual((255, 0 , 0), out_img.getpixel(DIFF_POS))
                self.assertEqual((0, 0, 0), out_img.getpixel((0, 0)))

    ###########################################################################
    ################################################################# modify ##
    ###########################################################################
    def test_modify(self):
        POS = (0, 0)
        for img in imgs.get_imgs():
            pixel = imgs.wrap(img.getpixel(POS))[0]
            evald_img = analyse.modify('value ^ 177', img)
            evald_pixel = imgs.wrap(evald_img.getpixel(POS))[0]
            self.assertEqual(evald_pixel, pixel ^ 177)

    def test_modify_output(self):
        img = imgs.get_imgs()[0]
        with imgs.TempFile() as tmp_path:
            analyse.modify('value ^ 177', img, out_path=tmp_path)
            self.assertTrue(os.path.isfile(tmp_path))

    ###########################################################################
    ################################################################ palette ##
    ###########################################################################
    def create_palette_img(self):
        img = Image.new(mode='L', size=(100, 100))
        img.putpalette(random.randint(0, 255) for _ in range(256 * 3))
        return img

    def test_fix_palette(self):
        img = self.create_palette_img()
        processed_img = analyse.fix_palette(img)
        palette = processed_img.getpalette()
        self.assertTrue(palette[0] == palette[1] == palette[2] == 0)
        self.assertTrue(palette[255 * 3] == palette[255 * 3 + 1]
                        == palette[255 * 3 + 2] == 255)

    def test_fix_palette_output(self):
        img = self.create_palette_img()
        with imgs.TempFile() as tmp_path:
            analyse.fix_palette(img, out_path=tmp_path)
            self.assertTrue(os.path.isfile(tmp_path))

    def test_fix_palette_no_palette(self):
        img = Image.new(mode='RGB', size=(100, 100), color=255)
        with self.assertRaisesRegexp(AssertionError, 'palette'):
            analyse.fix_palette(img)

    ###########################################################################
    ################################################################ strings ##
    ###########################################################################
    def test_find_strings_invalid_threshold(self):
        img = scipy.misc.lena()
        with imgs.TempFile(img) as path:
            with self.assertRaisesRegexp(AssertionError, '[tT]hreshold'):
                analyse.find_strings(img_path=path, threshold=0)
            with self.assertRaisesRegexp(AssertionError, '[tT]hreshold'):
                analyse.find_strings(img_path=path, threshold=-1)

    def test_iter_strings(self):
        MSG = 'This is a test'
        bits = np.unpackbits(np.array([ord(c) for c in MSG], dtype=np.uint8))
        strings = list(analyse.iter_strings(bits, 4))
        self.assertEqual(1, len(strings))
        self.assertEqual(MSG, strings[0])
        strings = list(analyse.iter_strings(bits, len(MSG) + 1))
        self.assertEqual(0, len(strings))


if __name__ == '__main__':
    unittest.main()
