__author__ = 'Jane'


# import modis_config.src.configuration as cfg
from multiprocessing import Process, Queue
import os
import shutil
from sci_data_records import SciDataRecords as SDR
# from osgeo import gdal
import sys
# if sys.platform == 'win32':
#     sys.path.append('C:\\Python27\\Scripts')


# gdal_vrtmerge.py has to be copied into a suitable place...
# e.g. C:\Python27\Lib\site-packages
# Code is here: https://svn.osgeo.org/gdal/trunk/gdal/swig/python/samples/gdal_vrtmerge.py
# Then some instructions on how to access it are here:
# http://gis.stackexchange.com/questions/118987/calling-gdal-merge-py-into-another-python-script-running-gdal-processes
import gdal_vrtmerge as gmerge

class GdalProcessing:
    def __init__(self):
        self.m_config = None

    def set_config_object(self, config):
        """
        Set up access to a configuration class instance which contains all the details needed.
        Must be done prior to any processing.

        :param config: a configuration:Configuration instance
        :return:
        """
        self.m_config = config
        self.m_sdr = SDR()

    def do_gdal_processing(self):
        # Check that data exists for required product/tile
        # Use the datastore directory from configuration
        source_dir = self.m_config.get_rawdata_dir()
        num_files = len([f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))])
        if num_files <= 0:
            print("No input data files found: check your source data path. Exiting.")
            raise IOError
        else:
            # now check that the files are the correct year and DoY
            # TODO use the shorthand method for string matching (as in distribute_gdal_work())
            for f in os.listdir(source_dir):
                if f.find(self.m_config.get_year) == -1:  # i.e. not found year substring
                    print("No files available for the required year. Exiting.")
                    raise IOError
                for doy in range(self.m_config.get_doy_range[0], self.m_config.get_doy_range[1] + 1):
                    if f.find(doy) != -1:
                        break  # i.e. found at least one DoY substring so we're good to go
                    else:
                        print("No files available for the required days. Exiting.")
                        raise IOError
            # we're through without an exception, therefore files of correct year/DoY are available to process
            self.distribute_gdal_work()

    def distribute_gdal_work(self):
        file_q = Queue()
        file_list = os.listdir(self.m_config.get_rawdata_dir())  # rawdata_dir includes /tile/product/
        # http://stackoverflow.com/questions/4843158/check-if-a-python-list-item-contains-a-string-inside-another-string
        year_match_list = [s for s in file_list if self.m_config.get_year in s]
        for doy in range(self.m_config.get_doy_range[0], self.m_config.get_doy_range[1] + 1):
            day_match_list = [s for s in year_match_list if str(doy) in s]
            if not day_match_list:
                print('not found doy ' + str(doy))
            else:
                # exclude the *.xml file
                the_file = [files for files in day_match_list if not "xml" in files][0]
                queue_item = (self.m_config.get_rawdata_dir() + the_file, doy)
                file_q.put(queue_item)
        for i in range(self.m_config.get_num_proc):
            p = Process(target=self.do_work, args=(file_q,))
            p.start()
        p.join()

    def do_work(self, q):
        while True:
            # create sub-dir based on pid, change to it
            temp_dir = self.m_config.get_rawdata_dir() + os.path.sep + os.getpid() + os.path.sep
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            os.chdir(temp_dir)

            # call gdal stuff
            queue_item = q.get()
            input_file = queue_item[0]   # returns string for file path-name
            doy = queue_item[1]
            for i_sdr in range(self.m_sdr.get_num_sdrs()):
                sdr_record = self.m_sdr.lookup_sdr_details(i_sdr)  # returns tuple with pixel size
                                                                   # & filename (e.g. sur_reflb05_1.vrt)
                pixel_size = sdr_record[0]
                out_file_name = sdr_record[1]
                # using Python's GDAL API is not straightforward and so use the native exe instead
                # see http://gis.stackexchange.com/questions/42584/how-to-call-gdal-translate-from-python-code
                if pixel_size == "500m":
                    os.system("gdal_translate -of VRT "
                              + self.m_sdr.get_sds_type()
                              + ':' + input_file + ':' + self.m_sdr.get_sdr(i_sdr)
                              + ' ' + out_file_name)
                else:
                    os.system("gdal_translate -of VRT -outsize 200% 200% "
                              + self.m_sdr.get_sds_type()
                              + ':' + input_file + ':' + self.m_sdr.get_sdr(i_sdr)
                              + ' ' + out_file_name)

            # Create reflectance layerstack - input file names taken from last SDR
            refl_string = '*' + self.m_sdr.get_gdalmerge_filenames()[0] + '*.vrt'
            sys.argv = ['-o', 'sur_refl.vrt', '-separate', refl_string]
            gmerge.main()
            # Create angular data layerstack
            zen_string = '*' + self.m_sdr.get_gdalmerge_filenames()[1] + '*vrt'
            az_string = '*' + self.m_sdr.get_gdalmerge_filenames()[2] + '*vrt'
            sys.argv = ['-o', 'angles.vrt', '-separate', zen_string, az_string]
            gmerge.main()

            # TODO now call another python script full of hardcoded values, eugh :(
            # python $HOME/MELODIES/src/MODIS/MOD09/MOD09GA.py

            # move results into central VRTs folder
            # mv $TMPDIR/SDS_layerstack_masked.tif $OUTDIR/$product.$year$strDoY.$tile.tif
            # mv $TMPDIR/SDS_layerstack_kernels_masked.tif $OUTDIR/$product.$year$strDoY.$tile.kernels.tif
            os.rename('SDS_layerstack_masked.tif',
                      self.m_config.get_gdal_dir() + self.m_config.get_product + '.'
                      + str(self.m_config.get_year) + str(doy) + '.'
                      + self.m_config.get_tile() + '.tif')
            os.rename('SDS_layerstack_kernels_masked.tif',
                      self.m_config.get_gdal_dir() + self.m_config.get_product + '.'
                      + str(self.m_config.get_year) + str(doy) + '.'
                      + self.m_config.get_tile() + '.kernels.tif')

            # remove the temporary files and process directory
            os.chdir('..')
            shutil.rmtree(temp_dir)