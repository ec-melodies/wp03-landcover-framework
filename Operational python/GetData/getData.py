__author__ = 'Jane'

import argparse
import sys
import landCoverDataProcess

def setup_args():
    """

    :return: Invocation arguments
    """
    # http://www.alanbriolat.co.uk/optional-positional-arguments-with-argparse.html
    parser = argparse.ArgumentParser()
    parser.add_argument('product',default='', nargs='?', help="Product name e.g. MOD09GA")
    parser.add_argument('year', default=-1, nargs='?', help="Year data required", type=int)
    parser.add_argument('tile', default='', nargs='?', help="Tile required")
    parser.add_argument('DoY', default=[], nargs='*', help="Start DoY and optionally also end DoY", type=int)
    return parser.parse_args()

def main():
    """


    """
    data_class = landCoverDataProcess.LandCoverDataProcess()
    args = setup_args()

    # test whether there are command line args
    # if not, get config
    if len(sys.argv) >= 4 :
        data_class.set_args (args.product, args.year, args.tile, args.DoY)
    else:
        try:
            data_class.read_config()
        except IOError:
            print("No config file: parameters must be provided instead. Exiting.")
            exit()
    data_class.download_data_files()




if __name__ == '__main__':
    main()