import argparse
import log
import numpy as np
import os


def parse_args(title, methods):
    """Create command line interface from data structure given in methods."""
    parser = argparse.ArgumentParser(description=title)
    parser.add_argument('-v', '--verbose', help='Verbose output',
                        action='store_true', default=False)
    sparser = parser.add_subparsers(title='methods')
    for method, data in methods.items():
        arguments = data.pop('arguments')
        function = data.pop('function')
        subparser = sparser.add_parser(method, help=function.__doc__)
        subparser.set_defaults(function=function)
        for argument in arguments:
            name_or_flags = ([argument.pop('name')] if 'name' in argument
                                                    else argument.pop('flags'))
            subparser.add_argument(*name_or_flags, **argument)
    return vars(parser.parse_args())


def start(title, methods):
    """Start the application and handle exceptions."""
    args = parse_args(title, methods)
    log.initialize(args.pop('verbose'))
    try:
        function = args.pop('function')
        log.debug('Starting %s with %s', function.__name__, args)
        function(**args)
        log.debug('Execution finish')
    except AssertionError as error:
        log.error(error)
    except Exception as error:
        log.exception(error)


def unpack_img_to_bits(img_array):
    return np.unpackbits(img_array.reshape((img_array.size, 1)), axis=1)


def pack_bits_to_img(img_bit_array, img_array):
    return np.packbits(img_bit_array, axis=1).reshape(img_array.shape)
