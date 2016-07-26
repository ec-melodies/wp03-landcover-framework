"""
constants.py contains constants which can be used by all modules
These are the defaults for all the settings used by the program, any of which
may be over-ridden but a basic set of product, tile, year and DoYis required
whether by individual arguments or contained within a JSON configuration file.
"""
__author__ = 'Jane'
import os

config_file_loc = str(os.getcwd()) + '/../../modis_config/land_cover_config.txt'

defs = {'all': [],
        'product': "",
        'tile': "",
        'year': -1,
        'DoY': [],
        'user': "",
        'passwd': "",
        'file': config_file_loc,
        'dir': ""}

# This is the number of the above settings which are stored in the JSON configuration file:
# current;y product, tile, year, DoY, dir, username and password
json_args = 7

local_time_zone = 'Europe/London'
