# SHIT - Stego Helper Identification Tool #
As steganography challenges get more popular in CTFs, we have to find a way to
deal with this shit. Introducing SHIT: It deals with this shit. It can either
create, read or analyse steganographic images, depending on your mood.

Don't, *I repeat*, don't try to create challenges with this tool. I am dead
serious.

Work in progress: Hopefully in an uncertain future it will analyse and solve
stego challenges. Maybe.

Here is a small documentation of our features. Don't forget: --help will always
give you a complete list of everything.


## Steganography Features ##
### LSB/MSB/Xth Bit ###

One common way of hiding data in images is to store it in the bits of the color
values. Especially overwriting the least significant bits of RGB values only
slightly affects the quality of the image and is not visible to the eye. Our
tool supports hiding and retrieving data with such techniques. You can choose
to store your data in every bit of the color values ranging from LSB to MSB.

Usage:

    $ hide.py bit 7 input.png stego.png 'Stego freakin sucks'  # 7 is the LSB
    $ retrieve.py bit 7 stego.png
    Stego freakin sucks
    $ hide.py bit 0 input.png stego.png 'Yep, it really does'  # 0 is the MSB
    $ retrieve.py bit 0 stego.png
    Yep, it really does


### Patchwork-like ###
This method chooses random pixels and stores a message in pixel value
differences.

Usage:

    $ hide.py patchwork input.png output.png 'Your totally awesome message'


## Steganalysis Features ##
### auto ###
This unfinished feature is meant to help you decide which analysis method you
should choose. Right now it only detects duplicate values in a color palette.

Usage:

    $ analyse.py auto stego.png


### combine ###
Combining two images may yield interesting results. For example, combining a
picture with steganographic messages inside with its original may uncover the
hidden message. Combine lets you choose a Python expression to combine the two
images (via numpy).

Usage:

    $ analyse.py combine 'img1 - img2' 1.png 2.png out.png  # sub two images
    $ analyse.py combine 'img1 ^ img2' 1.png 2.png out.png  # xor two images


### diff ###
certainly [find the hidden message][3]. The diff method will compare two images
pixel by pixel and output non-matching pixels with position and value. If the
images do not have the same mode (RGB, RGBA, ...) the original will be converted
to the mode of the steganographic image, although this may yield wrong results.

Usage:

    $ analyse.py diff original.png stego.png
    [INFO] Mismatched pixels at (5, 5): (0, 0, 0) vs (30, 30, 30)
    ...


### draw ###
Run a Xth bit steganographic analysis on the image and interpret the results as
an image (if bit is 1, draw a white pixel, else draw a black one). You can
specify a directory which will be filled with images of all planes and bands of
the image. This especially helps in challenges which were designed to be solved
with the StegSolve tool :-/

Usage:

    $ analyse.py draw stego.png output_dir


### modify ###
Some pictures hide information in an intelligently chosen [color palette][1] or
with extremely well chosen colors. An mask over every pixel value of the
image will shuffle these colors and may [unhide an hidden message][2]. Eval
allows you to execute an arbitrary python expression on each value of a pixel
separately.

Usage:

    $ analyse.py modify 'value^177' in.png out.png  # xor each value with 177
    $ analyse.py modify 'value-20' in.png out.png  # subtract 20 from each value


### palette ###
If a color palette was modified, [duplicate colors][1] can be used to hide
information. In order to counter this technique, SHIT can rewrite the whole
color palette to grayscale.

Usage:

    $ analyse.py palette stego.png stego.png output.png


### strings ###
This analysis method relies on you to know what you want. It quickly checks all
channels for LSB/MSB/xth bit stego and returns all strings containing 4
(configurable) or more printables it finds.

Usage:

    $ analyse.py strings stego.png  # default threshold is 4
    $ analyse.py strings --threshold 8 stego.png  # strings >= len 8
    $ analyse.py strings stego.png | grep flag  # and win, hopefully


[1]: https://github.com/ctfs/write-ups-2014/tree/master/plaid-ctf-2014/doge-stege
[2]: https://ucs.fbi.h-da.de/writeup-plaidctf-2014-doge-stege/
[3]: https://github.com/ctfs/write-ups-2014/blob/a0c08f898261cd1bd2deeaf03df892d7001b594d/asis-ctf-finals-2014/what-you-see/README.md
