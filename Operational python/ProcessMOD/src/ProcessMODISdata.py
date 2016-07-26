"""

"""
__author__ = 'Jane'

import sys
import argparse
import datetime as dt
#import LPDAAC_website as src
#import



def create_parser(args=None):
    """
    Set up and process arguments passed into program
    :param args: optional argument which defaults to nothing, only used in testing.
    :return: Invocation arguments
    """
    parser = argparse.ArgumentParser(description='Use 4 arguments with either -a switch or all switches to specify all '
                                                 'parameters, or select switch to override any parameter set in the '
                                                 'configuration file which may also be given. '
                                                 'Default file is ./land_cover_config.txt')
    parser.add_argument('-all', '-a', default=const.defs['all'], nargs=3, help="All three of year/tile/start_DoY "
                                                                               "in that order")
    parser.add_argument('-year', '-y', default=const.defs['year'], nargs='?', help="Year data required", type=int)
    parser.add_argument('-tile', '-t', default=const.defs['tile'], nargs='?', help="Tile required")
    parser.add_argument('-DoY', '-D', default=const.defs['DoY'], nargs='*',
                        help="Start Day of Year and optionally also end DoY", type=int)
    parser.add_argument('-src', '-s', default=const.defs['dir'], nargs='?',
                        help="Location for downloaded files, default is current directory")
    parser.add_argument('-dest', '-d', default=const.defs['dir'], nargs='?',
                        help="Location for output files, default is current directory")
    parser.add_argument('-proc', '-p', default=1, nargs='?', help="Number of processes to spawn", type=int)

    return parser.parse_args(args=args)


def main(args):
    pass



if __name__ == '__main__':
    parse_args = create_parser()
    main(parse_args)