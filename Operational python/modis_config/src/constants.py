"""
constants.py contains information which can be used by all modules.
"""
__author__ = 'Jane'
import os

# Constants for data retrieval
config_file = str(os.getcwd()) + '/../../modis_config/land_cover_config.ini'

defs = {'file': config_file,
        'dest': "VRTs"
        }

local_time_zone = 'Europe/London'

data_version = "005"

product_MOD = 'MOD'
product_MYD = 'MYD'
data_dir_MOD = "MOLT"
data_dir_MYD = "MOLA"
data_dir_other = "MOTA"
timestep_MOD = 1
timestep_MYD = 1
timestep_other = 8