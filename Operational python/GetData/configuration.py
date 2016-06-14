#######################################################
# 
# configuration.py
# Python implementation of the Class Configuration
# Generated by Enterprise Architect
# Created on:      24-May-2016 12:58:20
# Original author: Jane
# 
#######################################################

import datetime
import constants as const
import configFileManager

"""
NAME
    configuration - implementation of class
FILE
    configuration.py
CLASSES
    Configuration
"""


class Configuration:
    """
    Class to set up paths and URLs to find required data. Also dataset type and tile, plus
    time period. Requires a configFileManager object in constructor.

    Methods defined here:
        get_config(...)
            Loads config from file.

        set_args(...)
            Initialise config explicitly.

        get_tile(...)
            Retrieve tile name.

        create_filename(...)
            Concatenate parts to form file name.

        next_day(...)
            Iterate day used.

        is_valid_day(...)
            Check day in range of start-end.

        create_URL(...)
            Concatenate parts to from URL.

    ----------------------------------------------------------------------
    No data or other attributes defined here.

    """



    def __init__(self, mngr):
        """
        Initialise all attributes to empty values, keep pointer to the configFileManager.
        :param mngr: instantiated configFileManager object.
        :return: no return
        """
        self.m_ConfigFileManager = mngr
        self.m_config = const.defs['file']
        self.m_product = const.defs['product']
        self.m_tile = const.defs['tile']
        self.m_year = const.defs['year']
        self.m_DoY = const.defs['DoY']
        self.m_end_day = 0
        self.m_day_counter = 0

    def read_config(self, config_file):
        """
        Reads in saved configuration details.

        File handling is delegated: settings are retrieved and stored as instance
        attributes.

        :return: no return
        :raise: IOError if the config. file is not found.
        """
        try:
            self.m_config = config_file
            self.m_ConfigFileManager.load_config_file(config_file)  # this will raise exception if no data is available
            params = self.m_ConfigFileManager.get_config()
            self.set_args(params[0], params[1], params[2], params[3])
        except IOError:
            # if there is no saved config, need to tell the caller
            raise

    def write_config(self, config_file):
        """

        :param config_file:
        :return:
        """
        config_dict = {'product': self.m_product,
                       'tile': self.m_tile,
                       'year': self.m_year,
                       'DoY': self.m_DoY}
        self.m_ConfigFileManager.dump_config_file(config_file, config_dict)

    def get_tile(self):
        """
        Get instance property: tile name

        :return: tile name
        """
        return self.m_tile

    def set_args(self, product, year, tile, DoY):
        """
        Set instance properties for retrieving required data file.

        Data archive is at https://lpdaac.usgs.gov/dataset_discovery/modis/modis_products_table.
        If an end day of year is not specified, 365 is used. If any of the arguments is set to its
        default invalid value, the configuration file will be used to provide settings; if none provided,
        the default file will be loaded.

        :param product: MOD* and MYD* supported
        :param year: valid year in data archive
        :param tile: valid tile in data archive
        :param DoY: starting day of year, and optionally also end
        :raise IOError: if insufficient args and no config file to provide remainder
        :return: no return
        """
        # Read in the config file if any of these args is still a default (i.e. not set)
        # The config file will either be the default or will have been set to a new one
        # if the user has chosen to over-ride one or two args only.
        # However, if it's been set, its contents have already been loaded so we don't need to do it again.
        if ((product == const.defs['product']) or (year == const.defs['year']) or
                (tile == const.defs['tile']) or not DoY) and self.m_config == const.defs['file']:
            try:
                self.m_ConfigFileManager.load_config_file(self.m_config)
                params = self.m_ConfigFileManager.get_config()
            except IOError:
                raise

        # Then over-ride if non-default
        if product != const.defs['product']: self.m_product = product
        else: self.m_product = params[0]

        if year != const.defs['year']: self.m_year = year
        else: self.m_year = params[1]

        if tile != const.defs['tile']: self.m_tile = tile
        else: self.m_tile = params[2]

        if DoY != const.defs['DoY']: self.m_DoY = DoY
        else: self.m_DoY = params[3]

        self.m_day_counter = self.m_DoY[0]
        if len(self.m_DoY) == 2:
            self.m_end_day = self.m_DoY[1]
        else:
            self.m_end_day = 365
        self.__set_constants()

    def __set_constants(self):
        """
        Set instance properties for constants.
        :return: no return
        """
        self.m_version = "005"
        if str(self.m_product).startswith('MOD'):
            self.m_data_dir = "MOLT"
            self.m_time_step = 1
        elif str(self.m_product).startswith('MYD'):
            self.m_data_dir = "MOLA"
            self.m_time_step = 1
        else:
            self.m_data_dir = "MOTA"
            self.m_time_step = 8

    def create_local_filenames(self):
        """
        Construct name for retrieved files.

        Uses settings/parameters which define the file to be downloaded. Creates names for data and xml files.

        :return: file names for data and xml
        """
        local_filenames = []
        local_filename = (self.m_product + '.A' + str(self.m_year) + '{0:03d}'.format(self.m_day_counter) +
                          '.' + self.m_tile + '.' + self.m_version + '.hdf')
        local_filenames.append(local_filename)
        local_filename += str('.xml')
        local_filenames.append(local_filename)

        return local_filenames

    def is_valid_day(self):
        """
        Check whether the day of year is within the start-end range.

        :return: True if day is within range, False otherwise
        """
        print ("Day counter {}".format(self.m_day_counter))
        if self.m_day_counter <= self.m_end_day:
            return True
        else:
            return False

    def next_day(self):
        """
        Increments the day of year counter by the time step resolution.

        :return: no return
        """
        self.m_day_counter += self.m_time_step

    def create_URL(self):
        """
        Create the web page address to use.

        Uses settings/parameters which define the web page to access.

        :return: URL string
        """
        # convert current DoY into a date
        date = datetime.datetime(self.m_year, 1, 1) + datetime.timedelta(self.m_day_counter - 1)
        # create string
        web_string = ('http://e4ftl01.cr.usgs.gov/' + self.m_data_dir + '/' + self.m_product +
                      '.' + self.m_version + '/' + date.strftime('%Y.%m.%d'))
        return web_string



#    def set_time_period(self):
#         """
#
#         :return:
#         """
#         """Note Python datetime class can turn day of year into date:
#         > datetime.datetime(year, 1, 1) + datetime.timedelta(days - 1)
#         Then datetime methods to output in whatever format required.  or
#         > import datetime
#         > datetime.datetime.strptime('2010 120', '%Y %j')
#             datetime.datetime(2010, 4, 30, 0, 0)
#         > _.strftime('%d/%m/%Y')
#             '30/04/2010'
#         """
#        pass