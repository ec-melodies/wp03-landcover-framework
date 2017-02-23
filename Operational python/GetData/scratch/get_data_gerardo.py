#!/usr/bin/python

#Script based on:
# https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+Python

import os

from cookielib import CookieJar
from urllib import urlencode
import urllib2

# The user credentials that will be used to authenticate access to the data
username = "glopez22"
password = "GetMODIS00"
  
 
# The url of the file we wish to retrieve
 
url = "http://e4ftl01.cr.usgs.gov/MOLA/MYD09GA.005/2016.09.15/MYD09GA.A2016259.h18v04.005.2016261055634.hdf"
 
 
# Create a password manager to deal with the 401
# reponse that is returned from EarthData Login

url_login = "https://urs.earthdata.nasa.gov" 
password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
password_manager.add_password( None, url_login, username, password )
 
# Create a cookie jar for storing cookies. This is used to store and return
# the session cookie given to use by the data server (otherwise it will just
# keep sending us back to Earthdata Login to authenticate).  Ideally, we
# should use a file based cookie jar to preserve cookies between runs. This
# will make it much more efficient.
cookie_jar = CookieJar()

# Install all the handlers.
opener = urllib2.build_opener(
    urllib2.HTTPBasicAuthHandler(password_manager),
    #urllib2.HTTPHandler(debuglevel=1),    # Uncomment these two lines to see
    #urllib2.HTTPSHandler(debuglevel=1),   # details of the requests/responses
    urllib2.HTTPCookieProcessor(cookie_jar))

urllib2.install_opener(opener)
 
 
# Create and submit the request. There are a wide range of exceptions that
# can be thrown here, including HTTPError and URLError. These should be
# caught and handled.
request = urllib2.Request(url)
response = urllib2.urlopen(request)

# Get file
fname = os.path.basename( url )
binary_file = response.read()

f = open( fname, 'w' )
f.write( binary_file )
f.close()


 
