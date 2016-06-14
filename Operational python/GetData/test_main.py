"""
Test file

Also see http://dustinrcollins.com/testing-python-command-line-apps
and this for the clue to make arguments to pass in:
http://programmers.stackexchange.com/questions/220081/how-should-i-go-about-bringing-this-code-under-test
And the following link for how PyCharm is set up to use nosetests
https://www.jetbrains.com/help/pycharm/2016.1/run-debug-configuration-nose-test.html
"""

__author__ = 'Jane'

from getData import main, create_parser
from unittest import TestCase  # this needed to offer nosetests in PyCharm (bug!)
import nose.tools as ns

#  Test many of the command line options and their combinations.
def test_success_4_args():
    args = create_parser(['-all', "MOD09GA", "h18v04", "2007", "360"])
    # creates Namespace(all=['MOD09GA', 'h18v04', '2007', '360'])
    ns.assert_true(main(args, test_cmds=True))

@ns.raises(SystemExit)
def test_fail_4_args():
    args = create_parser(['-a', "MOD09GA", "h18v04", "360"])
    main(args, test_cmds=True)

def test_file_arg_file_exists():
    args = create_parser(['-file', 'my_config.txt'])
    ns.assert_true(main(args, test_cmds=True))

@ns.raises(SystemExit)
def test_file_arg_file_missing():
    args = create_parser(['-f', 'missing_file.txt'])
    main(args, test_cmds=True)

@ns.raises(EOFError)
def test_file_arg_file_wrong():
    args = create_parser(['-f', 'my_wrong_config.txt'])
    main(args, test_cmds=True)

def test_not_all_args_file_exists():
    args = create_parser(['-tile', "h17v03", '-year', '2005'])
    ns.assert_true(main(args, test_cmds=True))

@ns.raises(SystemExit)
def test_not_all_args_file_missing():
    args = create_parser(['-product', "MOD09GA", '-t', "h17v03", '-file', 'missing_file.txt'])
    main(args, test_cmds=True)

@ns.raises(EOFError)
def test_not_all_args_file_wrong():
    args = create_parser(['-p', "MOD09GA", '-t', "h17v03", '-f', 'my_wrong_config.txt'])
    main(args, test_cmds=True)

def test_file_save_default():
    args = create_parser(['-save', 'save_test_defaults.txt'])
    ns.assert_true(main(args, test_cmds=True))

def test_file_save():
    args = create_parser(['-tile', "h17v03", '-year', '2005', '-DoY', '200', '210', '-s', 'save_test_nondefaults.txt'])
    ns.assert_true(main(args, test_cmds=True))

#  Test a download, use the default config mostly as this is what's been set up in the page.
#  However, there is only a link for day 364, so need to specify start & end as day 364.
def test_file_download():
    args = create_parser(['-DoY', '364', '364', '-test', 'True'])
    ns.assert_false(main(args))