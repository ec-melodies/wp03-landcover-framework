#######################################################
# 
# configFileManager.py
# Python implementation of the Class ConfigFileManager
# Generated by Enterprise Architect
# Created on:      24-May-2016 12:59:39
# Original author: Jane
# 
#######################################################

import json
import constants as const

"""
NAME
    configFileManager - implementation of class
FILE
    configFileManager.py
CLASSES
    ConfigFileManager

NOT YET IMPLEMENTED
"""


class ConfigFileManager:
    """
    Class to get and set the configuration from a saved file in JSON format.

    Methods defined here:
        load_config_file(...)
            Read in saved configuration info.

        dump_config_file(...)
            Write configuration details to file.

        get_config(...)

    ----------------------------------------------------------------------
    No data or other attributes defined here.
    """

    def __init__(self):
        """

        :return: no return
        """
        self.m_product = const.defs['product']
        self.m_tile = const.defs['tile']
        self.m_year = const.defs['year']
        self.m_DoY = const.defs['DoY']

    def load_config_file(self, config_file):
        """
        Read in saved configuration info.
        If there isn't any, then pass exception up to caller.
        :return: no return
        """
        # self.m_config = config_file
        try:
            with open(config_file, 'r') as infile:
                config_dict = json.load(infile)
            # if it opens, check whether it's complete
            if len(config_dict) != const.json_args:
                raise EOFError
        except IOError as io_err:
            raise io_err

        self.m_product = config_dict['product']
        self.m_tile = config_dict['tile']
        self.m_year = config_dict['year']
        self.m_DoY = config_dict['DoY']

    def dump_config_file(self, config_file, config_dict):
        """
        Write configuration details to file.
        Can be used by Configuration class to save current details.

        :param config_file:
        :param config_dict:
        :return: no return
        """
        with open(config_file, 'w') as outfile:
            json.dump(config_dict, outfile)

    def get_config(self):
        """

        :return: retrieved settings
        """
        return self.m_product, self.m_year, self.m_tile, self.m_DoY
