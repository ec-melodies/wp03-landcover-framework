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
def test_success_6_args():
    args = create_parser(['-all', "MOD09GA", "2007", "h18v04", "360", "Melodies_test", "Testt35t"])
    # creates Namespace(all=['MOD09GA', 'h18v04', '2007', '360', 'Melodies_test', 'Testt35t'])
    ns.assert_true(main(args, testing_args=True))

@ns.raises(SystemExit)
def test_fail_4_args():
    args = create_parser(['-a', "MOD09GA", "h18v04", "360"])
    main(args, testing_args=True)

@ns.raises(EOFError)
def test_file_arg_file_exists_too_short():
    args = create_parser(['-file', 'my_config.txt'])
    main(args, testing_args=True)

def test_file_arg_file_exists():
    args = create_parser(['-file', 'my_login_config.txt'])
    ns.assert_true(main(args, testing_args=True))

@ns.raises(SystemExit)
def test_file_arg_file_missing():
    args = create_parser(['-f', 'missing_file.txt'])
    main(args, testing_args=True)

@ns.raises(EOFError)
def test_file_arg_file_wrong():
    args = create_parser(['-f', 'my_wrong_config.txt'])
    main(args, testing_args=True)

def test_not_all_args_file_exists():
    args = create_parser(['-tile', "h17v03", '-year', '2005'])
    ns.assert_true(main(args, testing_args=True))

@ns.raises(SystemExit)
def test_not_all_args_file_missing():
    args = create_parser(['-product', "MOD09GA", '-t', "h17v03", '-file', 'missing_file.txt'])
    main(args, testing_args=True)

@ns.raises(EOFError)
def test_not_all_args_file_wrong():
    args = create_parser(['-p', "MOD09GA", '-t', "h17v03", '-f', 'my_wrong_config.txt'])
    main(args, testing_args=True)

def test_file_save_default():
    args = create_parser(['-save', 'save_test_defaults.txt'])
    ns.assert_true(main(args, testing_args=True))

def test_file_save_posix():
    args = create_parser(['-tile', "h17v03", '-year', '2005', '-DoY', '200', '210', "-dir", "./data",
                          '-s', 'save_test_nondefaults.txt'])
    ns.assert_true(main(args, testing_args=True))


#  Test a download, use the default config mostly as this is what's been set up in the page.
#  However, there is only a link for day 364, so need to specify start & end as day 364.
def test_file_download():
    args = create_parser(['-D', '364', '364', '-test', 'Git'])
    ns.assert_false(main(args))

def test_download_location_posix():
    args = create_parser(['-D', '364', '364', '-test', 'Git', "-dir", "./data1"])
    ns.assert_false(main(args))

def test_download_location_windows():
    args = create_parser(['-D', '364', '364', '-test', 'Git', "-dir", ".\data2"])
    ns.assert_false(main(args))

#do real downloads... one with config login details, one with them provided
def test_real_file_download_login_via_file():
    args = create_parser(['-file', 'my_login_config.txt', '-D', '362', '362', '-test', 'Real'])
    ns.assert_false(main(args))

def test_real_file_download_login_direct():
    args = create_parser(['-user', 'Melodies_test', '-passwd', 'Testt35t', '-D', '364', '364', '-test', 'Real'])
    ns.assert_false(main(args))
