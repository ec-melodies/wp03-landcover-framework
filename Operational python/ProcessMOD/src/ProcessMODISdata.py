"""
ProcessMODISdata.py

Main program for processing MODIS raw data. This program is responsible for
* checking that processed files are not already present
* distributing files to process over user specified number of cores
* delegating actual processing to helper class

"""
__author__ = 'Jane'

import sys
import argparse
import modis_config.src.configuration as cfg
import modis_config.src.constants as cfg_const
import gdal_processing as proc

def create_parser(args=None):
    """
    Set up and process arguments passed into program
    :param args: optional argument which defaults to nothing, only used in testing.
    :return: Invocation arguments
    """
    parser = argparse.ArgumentParser(description='All configuration parameters are contained in ./land_cover_config.ini'
                                                 'Use -f switch to override with an alternative file.')
    parser.add_argument('-file', '-f', default=cfg_const.defs['file_proc'], nargs='?',
                        help="Name of configuration file to load")
    return parser.parse_args(args=args)


def main(args):
    """

    :param args: Namespace object containing given command line options

    :return: none
    :except: IOError if there is no configuration file
    :except: RuntimeError if configuration file is incomplete
    """
    config = cfg.Configuration()
    processing = proc.GdalProcessing()

    # Let's check the command line switches
    # if we're given a file, load the info.
    try:
        if args.file != cfg_const.defs['file']:
            config.read_config(1, args.file)
        else:
            config.read_config(1, cfg_const.defs['file'])
    except IOError:
        print("Missing configuration file. Exiting.")
        sys.exit(1)
    except RuntimeError:
        print("Configuration file has values missing. Exiting.")
        sys.exit(1)

    # pass config instance to gdal_processing
    processing.set_config_object(config)
    try:
        processing.do_gdal_processing()
    except IOError:
        sys.exit(1)

if __name__ == '__main__':
    parse_args = create_parser()
    main(parse_args)
