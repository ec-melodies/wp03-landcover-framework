#######################################################
# 
# webpageAccess.py
# Python implementation of the Class WebpageAccess
# Generated by Enterprise Architect
# Created on:      24-May-2016 12:58:37
# Original author: Jane
# 
#######################################################
import urllib2
"""
NAME
    webpageAccess - implementation of class
FILE
    webpageAccess.py
CLASSES
    WebpageAccess
"""

class WebpageAccess:
    """
    Class to retrieve data from archive.

    Methods defined here:
        retrieve_data_files(...)
            Loads config from file.

    ----------------------------------------------------------------------
    No data or other attributes defined here.


    """

    def __init__(self):
        """
        Set up a temporary file to contain web page text
        :return: no return
        """
        self.m_web_text_file_name = 'output.txt'

    def retrieve_data_files(self, address, tile, filename):
        """
        Download required data from archive website.

        + web address is assumed to be that of the archive
        + the tile must be valid in that it appears in the filename of available data
        + the destination filename will uniquely identify the data.

        :param address: archive web address
        :param tile: required tile
        :param filename: destination local file name
        :return: no return
        """
        # Get the file list from the pre-defined web page and put into temporary file
        self.__download_page(address, self.m_web_text_file_name)
        # Scan the list for the right entry
        file_to_download = self.__find_file_link(tile)
        # Download the data
        if file_to_download is not None:
            # get file
            self.__download_page(file_to_download, filename)
        else:
            # log if no file available
            pass

    @staticmethod
    def __download_page(address, destination_file):
        """
        Open the URL and read contents of the web page into the destination file.

        :param address: Valid URL
        :param destination_file: target local file
        :return: no return
        """
        try:
            response = urllib2.urlopen(address)
            with open(destination_file,'w') as f:
                f.write(response.read())
            f.close()
        except urllib2.URLError as URL_err:
            print ("Problem getting web page {}".format(URL_err.reason))

    def __find_file_link(self, tile):
        """
        Sub-sample file list for those conforming to search criteria.

        Webpage has already been selected based on product and date, so
        we are just looking for the correct tile, and the string must
        also contain both 'http' and '.hdf'

        :param tile:
        :return: link name or None
        """

        retval = None
        search_terms = ['http', '.hdf', tile]
        with open(self.m_web_text_file_name) as f:
            for line in f:
                if all(x in line for x in search_terms):
                    #  print (line)
                    #  print line.split()[1]
                    retval = line.split()[1]
        f.close()
        return retval


#
# with open("filename.txt") as f:
#     for line in f:
#         if "Smith" in line:
#              print line
#
# # Open file for reading
#         fo = open(search_path + fname)
#
#         # Read the first line from the file
#         line = fo.readline()
#
#         # Initialize counter for line number
#         line_no = 1
#
#         # Loop until EOF
#         while line != '' :
#                 # Search for string in line
#                 index = line.find(search_str)
#
# search_str = "hello"
# search_file = open("myfile", "r")
#
# for line in search_file:
#     if line.strip().find(search_str) != -1:
#         print line
#
# search_file.close()