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
from filecmp import cmp

import nose.tools as ns

from GetData.src.getData import main, create_parser, is_website_live
from modis_config.src.configuration import Configuration
from modis_config.src.constants import defs as constants

def setup():
    pass

# ensure the file system is clear of test and intermediate files/folders
def clean_up():
    try:
        for dr in glob.glob('.\data*'):
            shutil.rmtree(dr, ignore_errors=True)
        # for fl in glob.glob('.\*.hdf*'):
            # os.remove(fl)
        for dr in glob.glob(os.path.expanduser('~') + '\data'):
            shutil.rmtree(dr, ignore_errors=True)
        for fl in glob.glob('.\scrape.txt'):
            os.remove(fl)
    except Exception as ex:
        raise ex

def set_up_config(mode, the_file):
    config = Configuration()
    config.read_config(mode, the_file)
    return config

# Unit test some of the more complex methods
@ns.with_setup(teardown=clean_up)
def test_default_raw_folder():
    cfg = set_up_config(0, constants['file'])   # download mode
    # default dir is ~/data/[tile]/[product]
    # which will expand to [user]/data/h18v04/MOD09GA
    expected_folder = os.path.expanduser('~') + '\data\h18v04\MOD09GA' + os.path.sep
    ns.assert_equals(cfg.get_rawdata_dir(), expected_folder)

@ns.with_setup(teardown=clean_up)
def test_dwnld_section_raw_folder():
    cfg = set_up_config(0, 'land_cover_config_test_download_locPosix.ini')
    expected_folder = './data1\h18v04\MOD09GA' + os.path.sep
    ns.assert_equals(cfg.get_rawdata_dir(), expected_folder)

@ns.with_setup(teardown=clean_up)
def test_dflt_section_raw_folder():
    cfg = set_up_config(0, 'land_cover_config_test_download_locWin.ini')
    expected_folder = '.\data2\h18v04\MOD09GA' + os.path.sep
    ns.assert_equals(cfg.get_rawdata_dir(), expected_folder)

@ns.with_setup(teardown=clean_up)
def test_local_filenames():
    cfg = set_up_config(0, constants['file'])   # download mode
    expected_folder = os.path.expanduser('~') + '\data\h18v04\MOD09GA' + os.path.sep
    expected_filename1 = expected_folder + 'MOD09GA.A2007360.h18v04.005.hdf'
    expected_filename2 = expected_folder + 'MOD09GA.A2007360.h18v04.005.hdf.xml'
    files = cfg.create_local_filenames()
    ns.assert_equals(files, [expected_filename1, expected_filename2])

@ns.with_setup(teardown=clean_up)
def test_web_page_addr():
    cfg = set_up_config(0, constants['file'])   # download mode
    # products starting with 'MOD' require the 'MOLT' download area
    expected_web_addr = 'http://e4ftl01.cr.usgs.gov/MOLT/MOD09GA.005/2007.12.26'
    web_addr = cfg.create_URL()
    ns.assert_equals(web_addr, expected_web_addr)



# Test the configuration options and their combinations.
# setting 'testing_args' prevents any web access
@ns.with_setup(teardown=clean_up)
def test_success_default_ini_file():
    args = create_parser([])
    main(args, testing_args=True)
    # should have <user>/data/<tile>/<product> folder
    expected_path = os.path.expanduser('~') + os.path.sep + \
                    'data' + os.path.sep + 'h18v04' + os.path.sep + 'MOD09GA'
    ns.assert_true(os.path.exists(expected_path))

@ns.raises(SystemExit)
@ns.with_setup(teardown=clean_up)  # not that this is really needed here, but just in case...
def test_file_arg_file_missing_settings():
    args = create_parser(['-file', 'land_cover_config_missing_setting.ini'])
    main(args, testing_args=True)

@ns.raises(SystemExit)
@ns.with_setup(teardown=clean_up)  # or here either
def test_file_arg_file_missing():
    args = create_parser(['-f', 'missing_file.ini'])
    main(args, testing_args=True)


# Test a download, use the default config mostly as this is what's been set up in the page.
# setting test==Git uses the dummy website to scrape and dummy files to download.
# setting test==Real uses real website to scrape and real files to download but only the first 1000 bytes.
# The Git web page has only two files listed: an xml and hdf for product MOD, year 2007, tile h18v04, day 364.
@ns.with_setup(teardown=clean_up)
def test_file_download():
    args = create_parser(['-file', 'land_cover_config_test_download.ini', '-test', 'Git'])
    main(args)
    # should have a 'scrape.txt' locally, and <user>/data/<tile>/<product> with 2 files with test text
    expected_path = os.path.expanduser('~') + os.path.sep + \
                    'data' + os.path.sep + 'h18v04' + os.path.sep + 'MOD09GA'
    ns.assert_true(os.path.isfile(os.curdir + os.path.sep + 'scrape.txt'))
    ns.assert_true(os.path.isfile(expected_path + os.path.sep + 'MOD09GA.A2007364.h18v04.005.hdf'))
    ns.assert_true(os.path.isfile(expected_path + os.path.sep + 'MOD09GA.A2007364.h18v04.005.hdf.xml'))
    ns.assert_true(cmp(expected_path + os.path.sep + 'MOD09GA.A2007364.h18v04.005.hdf',
                       os.curdir + os.path.sep + 'git_test_MOD09GA.A2007364.h18v04.005.hdf'))
    ns.assert_true(cmp(expected_path + os.path.sep + 'MOD09GA.A2007364.h18v04.005.hdf.xml',
                       os.curdir + os.path.sep + 'git_test_MOD09GA.A2007364.h18v04.005.hdf.xml'))

@ns.with_setup(teardown=clean_up)
def test_download_location_posix():
    args = create_parser(['-file', 'land_cover_config_test_download_locPosix.ini', '-test', 'Git'])
    main(args)
    # should have a 'scrape.txt' locally, and ../data1/<tile>/<product> with 2 files with test text
    expected_path = os.curdir + os.path.sep + \
                    'data1' + os.path.sep + 'h18v04' + os.path.sep + 'MOD09GA'
    ns.assert_true(os.path.isfile(os.curdir + os.path.sep + 'scrape.txt'))
    ns.assert_true(os.path.isfile(expected_path + os.path.sep + 'MOD09GA.A2007364.h18v04.005.hdf'))
    ns.assert_true(os.path.isfile(expected_path + os.path.sep + 'MOD09GA.A2007364.h18v04.005.hdf.xml'))
    ns.assert_true(cmp(expected_path + os.path.sep + 'MOD09GA.A2007364.h18v04.005.hdf',
                       os.curdir + os.path.sep + 'git_test_MOD09GA.A2007364.h18v04.005.hdf'))
    ns.assert_true(cmp(expected_path + os.path.sep + 'MOD09GA.A2007364.h18v04.005.hdf.xml',
                       os.curdir + os.path.sep + 'git_test_MOD09GA.A2007364.h18v04.005.hdf.xml'))

@ns.with_setup(teardown=clean_up)
def test_download_location_windows():
    args = create_parser(['-file', 'land_cover_config_test_download_locWin.ini', '-test', 'Git'])
    main(args)
    # should have a 'scrape.txt' locally, and ../data2/<tile>/<product> with 2 files with test text - compare name & content
    expected_path = os.curdir + os.path.sep + \
                    'data2' + os.path.sep + 'h18v04' + os.path.sep + 'MOD09GA'
    ns.assert_true(os.path.isfile(os.curdir + os.path.sep + 'scrape.txt'))
    ns.assert_true(os.path.isfile(expected_path + os.path.sep + 'MOD09GA.A2007364.h18v04.005.hdf'))
    ns.assert_true(os.path.isfile(expected_path + os.path.sep + 'MOD09GA.A2007364.h18v04.005.hdf.xml'))
    ns.assert_true(cmp(expected_path + os.path.sep + 'MOD09GA.A2007364.h18v04.005.hdf',
                       os.curdir + os.path.sep + 'git_test_MOD09GA.A2007364.h18v04.005.hdf'))
    ns.assert_true(cmp(expected_path + os.path.sep + 'MOD09GA.A2007364.h18v04.005.hdf.xml',
                       os.curdir + os.path.sep + 'git_test_MOD09GA.A2007364.h18v04.005.hdf.xml'))

# do real download...
# must check if the website is live though!
@ns.with_setup(teardown=clean_up)
def test_real_file_download_login():
    if is_website_live():
        args = create_parser(['-file', 'land_cover_config_real_download.ini', '-test', 'Real'])
        main(args)
        # should have a 'scrape.txt' locally, and <user>/data/<tile>/<product> with 2 files with 1000 bytes real content
        expected_path = os.path.expanduser('~') + os.path.sep + \
                        'data' + os.path.sep + 'h18v04' + os.path.sep + 'MOD09GA'
        ns.assert_true(os.path.isfile(os.curdir + os.path.sep + 'scrape.txt'))
        ns.assert_true(os.path.isfile(expected_path + os.path.sep + 'MOD09GA.A2007362.h18v04.005.hdf'))
        ns.assert_true(os.path.isfile(expected_path + os.path.sep + 'MOD09GA.A2007362.h18v04.005.hdf.xml'))
    else:
        ns.assert_true(False, msg="Website down, unable to run test")

