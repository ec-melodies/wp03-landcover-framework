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

###########import landCoverDataManager
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
    parser = argparse.ArgumentParser(description='Use 6 arguments with either -a switch or all switches to specify all '
                                                 'parameters, or select switch to override any parameter set in the '
                                                 'configuration file which may also be given. '
                                                 'Default configuration file is ./land_cover_config.txt')
    parser.add_argument('-all', '-a', default=cfg_const.defs['all'], nargs=6,
                        help="All six of product/year/tile/start_DoY/username/password in that order")
    parser.add_argument('-product', '-p', default=cfg_const.defs['product'], nargs='?',
                        help="Product name e.g. MOD09GA")
    parser.add_argument('-year', '-y', default=cfg_const.defs['year'], nargs='?',
                        help="Year data required", type=int)
    parser.add_argument('-tile', '-t', default=cfg_const.defs['tile'], nargs='?',
                        help="Tile required")
    parser.add_argument('-DoY', '-D', default=cfg_const.defs['DoY'], nargs='*',
                        help="Start Day of Year and optionally also end DoY", type=int)
    parser.add_argument('-user', '-u', default=cfg_const.defs['user'], nargs='?',
                        help="Username to log into FTP site")
    parser.add_argument('-passwd', '-w', default=cfg_const.defs['passwd'], nargs='?',
                        help="Password to log into FTP site")
    parser.add_argument('-dir', '-d', default=cfg_const.defs['dir'], nargs='?',
                        help="Location for downloaded files, default is current directory")
    parser.add_argument('-file', '-f', default=cfg_const.defs['file'], nargs='?',
                        help="Name of configuration file to load")
    parser.add_argument('-save', '-s', nargs='?',
                        help="Name of file to save configuration settings")
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
    # if the program has been given the six args with the -a switch a bit like the original C-shell script's four
    # plus the new login details needed...
    if args.all:
        if len(args.all) != 6:
            print("Insufficient parameters provided with -a switch. Exiting.")
            sys.exit(1)
        else:
            # could trap exception of insufficient args and no config file but no need as already checked args
            config.set_args(args.all[0], args.all[1], args.all[2], args.all[3], args.all[4], args.all[5])
    # we're not expecting combinations of the above and anything else
    else:
        # if we're given a file, load the info.
        if args.file != cfg_const.defs['file']:
            try:
                config.read_config(args.file)
            except IOError:
                print("Missing or incorrect config file. Exiting.")
                sys.exit(1)
        # also we need to pick up any of the four basic settings (which will over-ride the file ones)
        # if the file has not been set (above), the config will load default file then override...
        if (args.product != cfg_const.defs['product']) or (args.year != cfg_const.defs['year']) or \
                (args.tile != cfg_const.defs['tile']) or (args.user != cfg_const.defs['user']) or \
                (args.passwd != cfg_const.defs['passwd']) or args.DoY:
            try:
                config.set_args(args.product, args.year, args.tile, args.DoY, args.user, args.passwd)
            except IOError:
                print("Insufficient parameters and no config file to provide defaults")
        # or we have no args at all (args.file has a default so can be used)
        else:
            try:
                    config.read_config(args.file)
            except IOError:
                print("No default config file: parameters must be provided instead. Exiting.")
                sys.exit(1)

    # if it's been given a destination for data download, ensure this is passed on
    if args.dir != cfg_const.defs['dir']:
        config.set_directory(args.dir)

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

    if args.save:
        config.write_config(args.save)

    return testing_args

if __name__ == '__main__':
    if is_website_live():
        parse_args = create_parser()
        main(parse_args)
    else:
        print (webpage_const.website_name + " website unavailable during its maintenance. Please try again later.")
