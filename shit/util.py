import argparse
import logging as log
import os


def configure_logging():
    log.basicConfig(level=log.DEBUG, format='[%(levelname)s] %(message)s')


def parse_args(title, methods):
    """Create command line interface from data structure given in methods."""
    parser = argparse.ArgumentParser(description=title)
    sparser = parser.add_subparsers(title='methods', dest='method')
    for method, data in methods.items():
        arguments = data.pop('arguments')
        subparser = sparser.add_parser(method, **data)
        for argument in arguments:
            name_or_flags = ([argument.pop('name')] if 'name' in argument
                                                    else argument.pop('flags'))
            subparser.add_argument(*name_or_flags, **argument)
    return vars(parser.parse_args())


def call_method(scope, args):
    """Call method given via command line in a given scope.

    The command line interface is built using a data structure. This implicitly
    defines which functions are available in a script and which arguments they
    take.
    """
    method = args.pop('method')
    scope[method](**args)


def start(title, methods, scope):
    """Start the application and handle exceptions."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    configure_logging()
    args = parse_args(title, methods)
    try:
        call_method(scope, args)
    except AssertionError as error:
        log.error(error)
    except Exception as error:
        log.exception(error)
