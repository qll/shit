#!/usr/bin/env python2

from scipy.misc import imread as read_img
from scipy.misc import imsave as save_image
import numpy as np
import random

def diff_methode(img_array, msg):
	msg_len = len(msg)
	x = random.randint(0, img_array.shape[0])
	y = random.randint(0, img_array.shape[1])

	key_array_A = []
	key_array_B = []

	while len(key_array_A) < msg_len:
		rand_pix = img_array[(random.randint(0, img_array.shape[0] - 1), random.randint(0, img_array.shape[1] - 1))]
		for p in img_array: 
			if rand_pix.all(p) and p not in key_array_A and rand_pix not in key_array_A and rand_pix not in key_array_B:
				key_array_A.append[rand_pix]
				key_array_B.append[p]

	print key_array_A
	print key_array_B

### TESTING ###
path = "C:\\Users\\Public\\Pictures\\Sample Pictures\\Koala.jpg"
path2 = "C:\\Users\\Public\\Pictures\\Sample Pictures\\KoalaTESTX.jpg"
img = read_img(path)
print img

msg = "This is a new diff methode for stego"

diff_methode(img, msg)