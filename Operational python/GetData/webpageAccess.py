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
        self.m_web_text_file_name = 'scrape.txt'

    def scrape_web_page(self, address):
        # Get the file list from the pre-defined web page and put into temporary file
        self.__download_page(address, self.m_web_text_file_name)

    def retrieve_data_files(self, archive_address, tile, local_filenames):
        """
        Download required data from archive website.

        + web address is assumed to be that of the archive
        + the tile must be valid in that it appears in the filename of available data
        + the destination filename will uniquely identify the data.

        :param archive_address: archive web address i.e. the one scraped for details of files
        :param tile: required tile
        :param filename: destination local file name
        :return: no return
        """

        # # Because the test website is slightly different, need to amend address by stripping page id from it
        # # 'http://www.resc.rdg.ac.uk/training/course_instructions.php/<the file to download>' is wrong!
        #if archive_address.endswith('.php'):
        #    archive_address = archive_address[:-len('/course_instructions.php')]
        if archive_address.find('git') != -1:
            archive_address =\
                'https://raw.githubusercontent.com/ec-melodies/wp03-landcover-framework/gh-pages'
        # Scan the list for the right entry
        files_to_download = self.__find_file_links(tile, archive_address)

        # Download the data and xml
        if len(files_to_download) >= 1:
            # get files
            local_file_ref = 0
            for target in files_to_download:
                self.__download_page(target, local_filenames[local_file_ref])
                local_file_ref += 1
        else:
            # TODO log if no file available
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
            with open(destination_file, 'w') as f:
                f.write(response.read())
        except urllib2.URLError as URL_err:
            print ("Problem getting web page data {}".format(URL_err.reason))

    def __find_file_links(self, tile, archive_address):
        """
        Sub-sample file list for those conforming to search criteria.

        Webpage has already been selected based on product and date, so
        we are just looking for the correct tile, and the string must
        also contain '.hdf' so will find two matches: one data, one xml.

        :param tile:
        :param archive_address: the parent archive web address
        :return: link names or empty array
        """

        retval = []
        search_terms = ['.hdf', tile]
        with open(self.m_web_text_file_name) as f:
            for line in f:
                if all(x in line for x in search_terms):
                    link = line.split()[5].split('\"')[1]
                    # this gives us the relative path, need to prepend http:\\ parent part
                    retval.append(archive_address + '/' + link)
                    if len(retval) == 2: # don't continue to search the text once the matches are found
                        break
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