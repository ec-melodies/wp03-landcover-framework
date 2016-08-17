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


# ensure the file system is clear of test and intermediate files/folders
def test_clean_up():
    try:
        for dr in glob.glob('.\data*'):
            shutil.rmtree(dr)
        for fl in glob.glob('.\*.hdf*'):
            os.remove(fl)
        for fl in glob.glob('.\save*'):
            os.remove(fl)
        os.remove('.\scrape.txt')
    except:
        pass

#  Test many of the command line options and their combinations.
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


#  Test a download, use the default config mostly as this is what's been set up in the page.
#  However, there is only a link for day 364, so need to specify start & end as day 364.
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

