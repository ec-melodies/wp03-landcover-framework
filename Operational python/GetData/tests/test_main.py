"""
Test file

Also see http://dustinrcollins.com/testing-python-command-line-apps
and this for the clue to make arguments to pass in:
http://programmers.stackexchange.com/questions/220081/how-should-i-go-about-bringing-this-code-under-test
And the following link for how PyCharm is set up to use nosetests
https://www.jetbrains.com/help/pycharm/2016.1/run-debug-configuration-nose-test.html
"""

__author__ = 'Jane'

import shutil
import os
import glob

import nose.tools as ns

from GetData.src.getData import main, create_parser
from modis_config.src.configuration import Configuration
from modis_config.src.constants import defs as constants


# ensure the file system is clear of test and intermediate files/folders
def test_clean_up():
    try:
        for dr in glob.glob('.\data*'):
            shutil.rmtree(dr)
        for fl in glob.glob('.\*.hdf*'):
            os.remove(fl)
        for fl in glob.glob('.\save*'):
            os.remove(fl)
        # TODO also need to remove files in user home directory
        os.remove('.\scrape.txt')
    except:
        pass

# Unit test some of the more complex methods
def set_up_config(mode, the_file):
    config = Configuration()
    config.read_config(mode, the_file)
    return config

def test_default_raw_folder():
    cfg = set_up_config(0, constants['file'])   # download mode
    # default dir is ~/data/[tile]/[product]
    # which will expand to [user]/data/h18v04/MOD09GA
    expected_folder = os.path.expanduser('~') + '\data\h18v04\MOD09GA' + os.path.sep
    ns.assert_equals(cfg.get_rawdata_dir(), expected_folder)

def test_dwnld_section_raw_folder():
    cfg = set_up_config(0, 'land_cover_config_test_download_locPosix.ini')
    expected_folder = './data1\h18v04\MOD09GA' + os.path.sep
    ns.assert_equals(cfg.get_rawdata_dir(), expected_folder)

def test_dflt_section_raw_folder():
    cfg = set_up_config(0, 'land_cover_config_test_download_locWin.ini')
    expected_folder = '.\data2\h18v04\MOD09GA' + os.path.sep
    ns.assert_equals(cfg.get_rawdata_dir(), expected_folder)

def test_local_filenames():
    cfg = set_up_config(0, constants['file'])   # download mode
    expected_folder = os.path.expanduser('~') + '\data\h18v04\MOD09GA' + os.path.sep
    expected_filename1 = expected_folder + 'MOD09GA.A2007360.h18v04.005.hdf'
    expected_filename2 = expected_folder + 'MOD09GA.A2007360.h18v04.005.hdf.xml'
    files = cfg.create_local_filenames()
    ns.assert_equals(files, [expected_filename1, expected_filename2])

def test_web_page_addr():
    cfg = set_up_config(0, constants['file'])   # download mode
    # products starting with 'MOD' require the 'MOLT' download area
    expected_web_addr = 'http://e4ftl01.cr.usgs.gov/MOLT/MOD09GA.005/2007.12.26'
    web_addr = cfg.create_URL()
    ns.assert_equals(web_addr, expected_web_addr)



# Test the configuration options and their combinations.
# setting 'testing_args' prevents any web access
def test_success_default_ini_file():
    args = create_parser([])
    ns.assert_true(main(args, testing_args=True))

@ns.raises(SystemExit)
def test_file_arg_file_missing_settings():
    args = create_parser(['-file', 'land_cover_config_missing_setting.ini'])
    ns.assert_true(main(args, testing_args=True))

@ns.raises(SystemExit)
def test_file_arg_file_missing():
    args = create_parser(['-f', 'missing_file.ini'])
    main(args, testing_args=True)


# Test a download, use the default config mostly as this is what's been set up in the page.
# setting test==Git uses the dummy website to scrape and dummy files to download.
# setting test==Real uses real website to scrape and real files but only the first 1000 bytes.
# TODO more detailed tests
def test_file_download():
    args = create_parser(['-file', 'land_cover_config_test_download.ini', '-test', 'Git'])
    ns.assert_false(main(args))

def test_download_location_posix():
    args = create_parser(['-file', 'land_cover_config_test_download_locPosix.ini', '-test', 'Git'])
    ns.assert_false(main(args))

def test_download_location_windows():
    args = create_parser(['-file', 'land_cover_config_test_download_locWin.ini', '-test', 'Git'])
    ns.assert_false(main(args))

# do real download...
def test_real_file_download_login():
    args = create_parser(['-file', 'land_cover_config_real_download.ini', '-test', 'Real'])
    ns.assert_false(main(args))

