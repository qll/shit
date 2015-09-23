# SHIT - Stego Helper Identification Tool #
As steganography challenges get more popular in CTFs, we have to find a way to
deal with this shit. Introducing SHIT: It deals with this shit. It can either
create, read or analyse steganographic images, depending on your mood.

Don't, *I repeat*, don't try to create challenges with this tool. I am dead
serious.

Work in progress: Hopefully in an uncertain future it will analyse and solve
stego challenges. Maybe.


## Steganalysis Features ##
### pixeldiff ###

If you find the unaltered original of a steganographic image you can almost
certainly find a hidden message. The pixeldiff method subtracts the values of
the original from the steganographic image. Non-zero values will be logged and
written to an output file if required.

Usage:

    analyse.py pixeldiff original.jpg stego.jpg
    analyse.py pixeldiff --output foo.jpg original.jpg stego.jpg
