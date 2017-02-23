__author__ = 'Jane'

import configparser
import os

cfg = configparser.ConfigParser()#allow_no_value=True)

config_file = str(os.getcwd()) + '/../../modis_config/land_cover_config.ini'

f=open(config_file)

cfg.read_file(f)

print cfg.defaults()

dsection = cfg['download']

print dsection.items()

msection = cfg['MODISprocess']

print msection.items()

print os.path.basename(os.path.curdir)

print os.path.expanduser('~')