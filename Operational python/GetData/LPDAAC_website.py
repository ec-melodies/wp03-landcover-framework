"""
LPDAAC_website.py contains all the specific details for downloading data archive
files from the repository.
The https://lpdaac.usgs.gov/data_access/data_pool site declares site downtime as
every Wednesday 0800-1200 Central Time for weekly maintenance.
"""
__author__ = 'Jane'

website_name = 'LP DAAC'
down_day = 'Wednesday'
down_time_start = 8
down_time_end = 12
down_time_zone = 'US/Central'
data_addr_root = 'http://e4ftl01.cr.usgs.gov/'
data_file_ext = 'hdf'
data_files_to_retrieve = 2

# Files appear on the parent listing page with entries like this (on one line):
# <img src="/icons/unknown.gif" alt="[   ]"> <a href="MOD09GA.A2007364.h18v04.005.2008001234502.hdf">
#                              MOD09GA.A2007364.h18v04.005.2008001234502.hdf</a> 2009-04-20 20:21 89M
# so to find the actual file name, we need to split the string on spaces to give:
# ['<img',
#  'src="/icons/unknown.gif"',
#  'alt="[',
#  ']">',
#  '<a',
#  'href="MOD09GA.A2007364.h18v04.005.2008001234502.hdf">MOD09GA.A2007364.h18v04.005.2008001234502.hdf</a>',
#  '2009-04-20',
#  '20:21',
#  '89M']
#
# get the 6th (or 5th starting at zero), and subsequently split it on double quote marks to give:
# ['href=',
#  'MOD09GA.A2007364.h18v04.005.2008001234502.hdf',
#  '>MOD09GA.A2007364.h18v04.005.2008001234502.hdf</a>']
#
# from which we want the 2nd (or 1st starting at zero) string
line_split_1 = 5
line_split_2 = 1