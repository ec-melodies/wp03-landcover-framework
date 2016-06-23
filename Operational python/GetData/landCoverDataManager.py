#######################################################
# 
# landCoverDataProcess.py
# Python implementation of the Class LandCoverDataProcess
# Generated by Enterprise Architect
# Created on:      24-May-2016 12:58:29
# Original author: Jane
# 
#######################################################

import os
import configFileManager
import configuration
import webpageAccess

"""
NAME
    LandCoverDataProcess - implementation of class
FILE
    landCoverDataProcess.py
CLASSES
    landCoverDataProcess
"""

class LandCoverDataManager:
    # TODO Allow product to be specified in different ways (Terra/Aqua/MOD/MYD/combined).
    """
    Manager class to organise all the tasks.

    Will need to know location of any XML config file, and/or tile, datetime and
    product.


    Methods defined here:
        set_args(...)
            Set up the data file identifiers.

        read_config(...)
            Restore data file identifiers from user's file.

        download_data_files(...)
            Retrieves all data files specified.

    ----------------------------------------------------------------------
    No data or other attributes defined here.

    """
    def __init__(self):
        """
        Initialise all managed objects
        :return:
        """
        self.m_ConfigFileManager= configFileManager.ConfigFileManager()
        self.m_Configuration = configuration.Configuration(self.m_ConfigFileManager)
        self.m_WebpageAccess = webpageAccess.WebpageAccess()

    def set_args(self, product, year, tile, doy):
        """
        Set up the data file identifiers: properties for retrieving required data file.

        This is delegated to the Configuration class.

        :param product: MOD* and MYD* supported
        :param year: valid year in data archive
        :param tile: valid tile in data archive
        :param doy: starting day of year, and optionally also end
        :raise IOError: if insufficient args and no config file to provide remainder
        :return: no return
        """
        try:
            self.m_Configuration.set_args(product, year, tile, doy)
        except IOError as io_err:
            raise io_err

    def set_directory(self, dir):
        """
        Set the location of all downloaded data files.
        This does not affect the location of configuration files which are
        assumed to be in the same location as the program.
        :param dir: directory to store all downloaded files
        :return:
        """
        self.m_Configuration.set_directory(dir)

    def read_config(self, config_file):
        """
        Restore data file identifiers from user's configuration file.

        This is delegated to the Configuration class.
        :return: no return
        :raise: IOError if the default config. file is not found.
        """
        try:
            self.m_Configuration.read_config(config_file)
        except IOError as io_err:
            print("Exception: {}: {}".format(io_err.strerror, io_err.filename))
            raise io_err
        except Exception:
            raise

    def write_config(self, config_file):
        """

        :param config_file:
        :return:
        """
        self.m_Configuration.write_config(config_file)

    def download_data_files(self, test_mode):
        """
        Retrieves all data files specified.

        :param test_mode: controls webpage accessed for testing purposes.
        :return: no return
        """
        # set up the correct web page dependent on mode
        if test_mode:
            parent_web_page = "http://ec-melodies.github.io/wp03-landcover-framework/"
            #parent_web_page = "http://www.resc.rdg.ac.uk/training/course_instructions.php"
        else:
            parent_web_page = self.m_Configuration.create_URL()

        # get the contents of the parent web page
        if self.m_Configuration.is_valid_day():
            self.m_WebpageAccess.scrape_web_page(parent_web_page)

        # while DoY not at the finish
        while self.m_Configuration.is_valid_day():
            # convert the args to filename strings for data and xml - use config class
            local_filenames = self.m_Configuration.create_local_filenames()

            # check whether the files have already been downloaded
            for target in local_filenames:
                if os.path.isfile('./' + target):
                    print("File already exists {}".format(target))
                    raise RuntimeError("File already exists {}".format(target))

            self.m_WebpageAccess.retrieve_data_files(parent_web_page, self.m_Configuration.get_tile(), local_filenames)

        # increment to next DoY
        self.m_Configuration.next_day()