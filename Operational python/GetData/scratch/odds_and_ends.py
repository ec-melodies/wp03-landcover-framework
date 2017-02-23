__author__ = 'Jane'
import os
import urllib2
import base64
import cookielib

# if sys.platform == 'win32':
#     sys.path.append('C:\\Python27\\Scripts')

#
# full = os.listdir('C:\Users\Jane\data\h18v04\MOD09GA')
# yearmatch = [s for s in full if '2007' in s]
# print yearmatch
#
# for i in range(361, 364 +1):
#     daymatch=[s for s in yearmatch if str(i) in s]
#     if not daymatch:
#         print('not found ' + str(i))
#     else:
#         print('found ' + str(i))
#         print daymatch[0]
#         print daymatch[1]
#         the_file = [files for files in daymatch if not "xml" in files][0]
#         print ('hdf file only: ' + the_file)

        # # Because the test website is slightly different, need to amend address by stripping page id from it
        # # 'http://www.resc.rdg.ac.uk/training/course_instructions.php/<the file to download>' is wrong!
        #if archive_address.endswith('.php'):
        #    archive_address = archive_address[:-len('/course_instructions.php')]

url = "http://e4ftl01.cr.usgs.gov/MOLT/MOD09GA.005/2000.03.12/MOD09GA.A2000072.h14v02.005.2008237034113.hdf.xml"
request = urllib2.Request(url)
base64string = base64.b64encode('%s:%s' % ('Melodies_test', 'Testt35t'))
request.add_header("Authorization", "Basic %s" % base64string)
# response = urllib2.urlopen(request)
# opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
# resp = opener.open(request)
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
resp = opener.open(request)


with open(os.path.basename(url), 'w') as f:
    f.write(resp.read(1000))

#    def set_time_period(self):
#         """
#
#         :return:
#         """
#         """Note Python datetime class can turn day of year into date:
#         > datetime.datetime(year, 1, 1) + datetime.timedelta(days - 1)
#         Then datetime methods to output in whatever format required.  or
#         > import datetime
#         > datetime.datetime.strptime('2010 120', '%Y %j')
#             datetime.datetime(2010, 4, 30, 0, 0)
#         > _.strftime('%d/%m/%Y')
#             '30/04/2010'
#         """
#        pass

