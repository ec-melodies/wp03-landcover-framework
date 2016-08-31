__author__ = 'Jane'
import shutil
import os
import glob

import nose.tools as ns

from ProcessMOD.src.processMODISdata import main, create_parser
from modis_config.src.configuration import Configuration
from modis_config.src.constants import defs as constants

def set_up_config(mode, the_file):
    config = Configuration()
    config.read_config(mode, the_file)
    return config

def test_success_default_ini_file():
    args = create_parser([])
    ns.assert_true(main(args))

def test_gdal_default_folder():
    cfg = set_up_config(1, constants['file'])   # process mode
    expected_folder = os.path.expanduser('~') + '\data\h18v04\MOD09GA' + os.path.sep + 'VRTs' + os.path.sep
    ns.assert_equals(cfg.get_gdal_dir(), expected_folder)

def test_gdal_prcs_section_folder():
    cfg = set_up_config(1, 'land_cover_config_test_gdal.ini')   # process mode
    expected_folder = '.\gdal_files' + os.path.sep
    ns.assert_equals(cfg.get_gdal_dir(), expected_folder)