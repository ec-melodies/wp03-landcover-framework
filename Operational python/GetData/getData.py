"""
getData.py
Main script for downloading land cover data files.

Note on testing: test framework uses optional arg to main() to mimic full behaviour but stop short of
download from the data archive. In addition, command line arg '-test' is used to do a download from
a dummy website.
"""
__author__ = 'Jane'

import sys
import argparse
import landCoverDataManager
import constants as const

def create_parser(args=None):
    """

    :return: Invocation arguments
    """
    # http://www.alanbriolat.co.uk/optional-positional-arguments-with-argparse.html
    parser = argparse.ArgumentParser(description='Use 4 arguments with either -a switch or all switches to specify all '
                                                 'parameters, or select switch to override any parameter set in the '
                                                 'configuration file which may also be given. '
                                                 'Default file is ./land_cover_config.txt')
    parser.add_argument('-all', '-a', default=const.defs['all'], nargs=4, help="All four of product/year/tile/DoY "
                                                                               "in that order")
    parser.add_argument('-product', '-p', default=const.defs['product'], nargs='?', help="Product name e.g. MOD09GA")
    parser.add_argument('-year', '-y', default=const.defs['year'], nargs='?', help="Year data required", type=int)
    parser.add_argument('-tile', '-t', default=const.defs['tile'], nargs='?', help="Tile required")
    parser.add_argument('-DoY', '-D', default=const.defs['DoY'], nargs='*',
                        help="Start Day of Year and optionally also end DoY", type=int)
    parser.add_argument('-dir', '-d', default=const.defs['dir'], nargs='?',
                        help="Location for downloaded files, default is current directory")
    parser.add_argument('-file', '-f', default=const.defs['file'], nargs='?', help="Name of configuration file to load")
    parser.add_argument('-save', '-s', nargs='?', help="Name of file to save configuration settings")
    parser.add_argument('-test', default=False, nargs='?', help="Run program in test mode, development only")
    return parser.parse_args(args=args)

def main(args, test_cmds=False):
    """

    :param args: Namespace object containing given command line options
    :param test_cmds: Optional parameter which, if true, will prevent data download
    :return: value of test_cmds
    """
    # Create class which will handle all the details
    data_manager = landCoverDataManager.LandCoverDataManager()

    # Let's check the command line switches
    # if the program has been given the four args with the -a switch a bit like the original C-shell script.
    if args.all:
        if len(args.all) != 4:
            print("Insufficient parameters provided. Exiting.")
            sys.exit(1)
        else:
            # could trap exception of insufficient args and no config file but no need as already checked args
            data_manager.set_args(args.all[0], args.all[1], args.all[2], args.all[3])
    # we're not expecting combinations of the above and anything else
    else:
        # if we're given a file, load the info.
        if args.file != const.defs['file']:
            try:
                data_manager.read_config(args.file)
            except IOError:
                print("Missing or incorrect config file. Exiting.")
                sys.exit(1)
        # also we need to pick up any of the four basic settings (which will over-ride the file ones)
        if (args.product != const.defs['product']) or (args.year != const.defs['year']) or \
                (args.tile != const.defs['tile']) or args.DoY:
            try:
                data_manager.set_args(args.product, args.year, args.tile, args.DoY)
            except IOError:
                print("Insufficient parameters and no config file to provide defaults")
        # or we have no args at all (args.file has a default so can be used)
        else:
            try:
                    data_manager.read_config(args.file)
            except IOError:
                print("No default config file: parameters must be provided instead. Exiting.")
                sys.exit(1)

    # if it's been given a destination for data download, ensure this is passed on
    if args.dir != const.defs['dir']:
        data_manager.set_directory(args.dir)


    try:
        if not test_cmds:
            try:
                data_manager.download_data_files(args.test)
            except RuntimeError as r_err:
                print(r_err.message)

    except Exception as err:
        print err.message

    if args.save:
        data_manager.write_config(args.save)

    return test_cmds

if __name__ == '__main__':
    parse_args = create_parser()
    main(parse_args)
