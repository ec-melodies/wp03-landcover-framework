"""
getData.py
Main program for downloading land cover data files.

Note on testing: test framework uses optional arg to main() to mimic full behaviour but stop short of
download from the data archive. In addition, command line arg '-test' is used to do a download from
a dummy website.
"""
__author__ = 'Jane'

import sys
import datetime as dt
import calendar
import argparse

import pytz

import modis_config.src.constants as cfg_const
import modis_config.src.configuration as cfg
import LPDAAC_website as webpage_const
import webpageAccess


def is_website_live():
    """
    Check the day and time.
    Use the parameters in the website configuration file: LPDAAC_website.py
    :return: True if site is up and operational.
    """
    now_day = dt.date.today()
    # firstly check if it's a Wednesday
    if webpage_const.down_day == calendar.day_name[now_day.weekday()]:
        # check the time, allowing for the time zone
        now = dt.datetime.now(pytz.timezone(cfg_const.local_time_zone))
        # pytz.all_timezones gives list of valid strings
        central = pytz.timezone(webpage_const.down_time_zone)
        start = dt.time(webpage_const.down_time_start, 0, 0, 0, central)
        end = dt.time(webpage_const.down_time_end, 0, 0, 0, central)
        now_converted = now.astimezone(central)
        if start <= now_converted <= end:
            return False
    else:
        return True


def create_parser(args=None):
    """

    :return: Invocation arguments
    """
    # http://www.alanbriolat.co.uk/optional-positional-arguments-with-argparse.html
    parser = argparse.ArgumentParser(description='All configuration parameters are contained in ./land_cover_config.ini'
                                                 'Use -f switch to override with an alternative file.')

    parser.add_argument('-file', '-f', default=cfg_const.defs['file'], nargs='?',
                        help="Name of configuration file to load")
    parser.add_argument('-test', default='No', nargs='?',
                        help="Run program in test mode, development only")
    return parser.parse_args(args=args)

def main(args, testing_args=False):
    """

    :param args: Namespace object containing given command line options
    :param testing_args: Optional parameter which, if true, will prevent data download. Used by automated testing only.
    :return: value of test_cmds
    """
    # Create classes which will handle all the details
    config = cfg.Configuration()
    web = webpageAccess.WebpageAccess()

    # Let's check the command line switches
    # if we're given a file, load the info. otherwise load the default one anyway
    try:
        if args.file != cfg_const.defs['file']:
            config.read_config(0, args.file)
        else:
            config.read_config(0, cfg_const.defs['file'])
    except IOError:
        print("Missing configuration file. Exiting.")
        sys.exit(1)
    except RuntimeError:
        print("Configuration file has values missing. Exiting.")
        sys.exit(1)

    web.set_config_object(config)

    try:
        if not testing_args:
            try:
                # args.test controls whether this is a real download or one instigated by the auto-testing.
                web.download_data_files(args.test)
            except RuntimeError as r_err:
                print(r_err.message)

    except Exception as err:
        print err.message

    # if args.save:
    #     config.write_config(args.save)

    return testing_args

if __name__ == '__main__':
    if is_website_live():
        parse_args = create_parser()
        main(parse_args)
    else:
        print (webpage_const.website_name + " website unavailable during its maintenance. Please try again later.")
