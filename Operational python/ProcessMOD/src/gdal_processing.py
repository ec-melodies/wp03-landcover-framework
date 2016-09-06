__author__ = 'Jane'


import os
import shutil
import sys
import subprocess
from multiprocessing import Process, Queue
from sci_data_records import SciDataRecords as SDR
from sci_data_records import File_index
import dataset_info as di

# gdal_vrtmerge.py has to be copied into a suitable place...
# e.g. C:\Python27\Lib\site-packages
# Code is here: https://svn.osgeo.org/gdal/trunk/gdal/swig/python/samples/gdal_vrtmerge.py
# Then some instructions on how to access it are here:
# http://gis.stackexchange.com/questions/118987/calling-gdal-merge-py-into-another-python-script-running-gdal-processes
#   import gdal_vrtmerge as gmerge
#   sys.argv = ['-o', self.m_sdr.get_refl_filename, '-separate', refl_filename_string]
#   gmerge.main()
# WHICH DON'T WORK!!!   using subprocess instead with addition of path info.
import gdal_vrtmerge

class GdalProcessing:
    """
    Class to oversee image processing.

    Methods defined here:
        set_config_object(...)
            Set up access to a configuration class instance which contains all the details needed.

        do_gdal_processing(...)
            Main work of class: ensure files are available and instigate processing.

    ----------------------------------------------------------------------
    No data or other attributes defined here.
    """
    def __init__(self):
        self.m_config = None

    def set_config_object(self, config):
        """
        Set up access to a configuration class instance which contains all the details needed.
        Must be done prior to any processing.

        :param config: a configuration:Configuration instance
        :return: no return
        """
        self.m_config = config
        self.m_sdr = SDR()

    def do_gdal_processing(self, test_mode):
        """
        Main work of class: ensure files are available and instigate processing.
        :return: no return
        """
        # Check that data exists for required product/tile
        # Use the datastore directory from configuration
        source_dir = self.m_config.get_rawdata_dir()
        num_files = len([f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))])
        if num_files <= 0:
            print("No input data files found: check your source data path. Exiting.")
            raise IOError
        else:
            # now check that the files are the correct year and DoY
            # see http://stackoverflow.com/questions/9038160/break-two-for-loops for logic
            # TODO use the shorthand method for string matching (as in distribute_gdal_work())
            for f in os.listdir(source_dir):
                if f.find(str(self.m_config.get_year())) == -1:  # i.e. not found year substring
                    print("No files available for the required year. Exiting.")
                    raise IOError
                for doy in range(self.m_config.get_doy_range()[0], self.m_config.get_doy_range()[1] + 1):
                    if f.find(str(doy)) != -1:
                        break  # i.e. found at least one DoY substring so we're good to go
                    else:
                        print("No files available for the required days. Exiting.")
                        raise IOError
                else:
                    continue
                break
            # we're through without an exception, therefore files of correct year/DoY are available to process
            if not test_mode:
                self._distribute_gdal_work()

    def _distribute_gdal_work(self, testing=False):
        """
        Put files matching required days onto a queue and spawn processes.

        Each queue item contains both the file and its DoY. Only the hdf files are added.
        The number of processes spawned is controlled by 'nproc' in the configuration file,
        and this method will wait until all have finished.
        :return: no return
        """
        file_q = Queue()
        file_list = os.listdir(self.m_config.get_rawdata_dir())  # rawdata_dir includes /tile/product/
        # http://stackoverflow.com/questions/4843158/check-if-a-python-list-item-contains-a-string-inside-another-string
        year_match_list = [s for s in file_list if str(self.m_config.get_year()) in s]
        print ('Searching for raw data in ' + self.m_config.get_rawdata_dir())
        for doy in range(self.m_config.get_doy_range()[0], self.m_config.get_doy_range()[1] + 1):
            day_match_list = [s for s in year_match_list if str(doy) in s]
            if not day_match_list:
                print('not found doy ' + str(doy))
            else:
                # exclude the *.xml file
                the_file = [files for files in day_match_list if not "xml" in files][0]
                queue_item = (self.m_config.get_rawdata_dir() + the_file, doy)
                file_q.put(queue_item)
        if not testing:
            for i in range(self.m_config.get_num_proc()):
                p = Process(target=self._do_work, args=(file_q,))
                p.start()
            p.join()
        else:
            return file_q

    def _do_work(self, q, testing=False):
        """
        File processing: do GDAL translate then call layerstack & QA methods

        Work in a unique folder to retrieve image file and call GDAL translation for each of
        the pre-defined scientific data records in class SciDataRecords.
        Continue with further processing on the GDAL datasets.

        :param q: the queue of items to process (filename and its DoY)
        :return: no return
        """

        while True:
            # create sub-dir based on pid, change to it
            temp_dir = self.m_config.get_rawdata_dir() + os.path.sep + str(os.getpid()) + os.path.sep
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            os.chdir(temp_dir)

            if testing:
                the_file = open('_do_work.txt', mode='w')

            # retrieve queue item: file and its DoY
            queue_item = q.get()
            input_file = queue_item[0]   # returns string for file path-name
            doy = queue_item[1]
            for i_sdr in range(self.m_sdr.get_num_sdrs()):
                sdr_record = self.m_sdr.lookup_sdr_details(i_sdr)  # returns tuple with pixel size
                                                                   # & filename (e.g. sur_reflb05_1.vrt)
                pixel_size = sdr_record[0]
                out_file_name = sdr_record[1]
                if not testing:
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
                else:   # testing
                    # put output into the text file
                    if pixel_size == "500m":
                        the_file.write("gdal_translate -of VRT "
                                       + self.m_sdr.get_sds_type()
                                       + ':' + input_file + ':' + self.m_sdr.get_sdr(i_sdr)
                                       + ' ' + out_file_name + '\n')
                    else:
                        the_file.write("gdal_translate -of VRT -outsize 200% 200% "
                                       + self.m_sdr.get_sds_type()
                                       + ':' + input_file + ':' + self.m_sdr.get_sdr(i_sdr)
                                       + ' ' + out_file_name + '\n')

            if not testing:
                # Continue processing file set...
                self._create_layerstacks(temp_dir)

                # Create object to handle details
                dataset_info = di.DatasetInfo(temp_dir)

                self._process_layerstacks(dataset_info)

                self._calculate_kernels(dataset_info)

                self._move_results(temp_dir, doy)

            else:
                the_file.close()
                # ensure we exit this method when in test mode
                return temp_dir, the_file.name




    def _create_layerstacks(self, temp_dir):
        """
        Create layerstacks from translated image files.

        Process reflectance and angles files separately.

        :param temp_dir: working directory
        :return: no return
        """
        try:
            os.chdir(temp_dir)
            # firstly, make sure we can access gdal_vrtmerge.py
            merge_path = os.path.dirname(gdal_vrtmerge.__file__)

            # Create reflectance layerstack - match all sur_refl files
            refl_filename_string = '*' + self.m_sdr.get_gdalmerge_filenames()[File_index.sur_refl] + '*.vrt'
            print ('gdal_processing._create_layerstacks(): python ' + merge_path + os.path.sep + 'gdal_vrtmerge.py -o '
                   + self.m_sdr.get_refl_filename() + ' -separate ' + refl_filename_string)
            subprocess.check_call('python ' + merge_path + os.path.sep + 'gdal_vrtmerge.py -o ' +
                                  self.m_sdr.get_refl_filename() +
                                  ' -separate ' + refl_filename_string)

            # Create angular data layerstack - match all Zen files then all Az files
            zen_filename_string = '*' + self.m_sdr.get_gdalmerge_filenames()[File_index.Zenith] + '*vrt'
            az_filename_string = '*' + self.m_sdr.get_gdalmerge_filenames()[File_index.Azimuth] + '*vrt'
            print ('gdal_processing._create_layerstacks(): python ' + merge_path + os.path.sep + 'gdal_vrtmerge.py -o '
                   + self.m_sdr.get_agl_filename() + ' -separate ' + zen_filename_string + az_filename_string)
            subprocess.check_call('python ' + merge_path + os.path.sep + 'gdal_vrtmerge.py -o ' +
                                  self.m_sdr.get_agl_filename() +
                                  ' -separate ' + zen_filename_string + az_filename_string)

        except subprocess.CalledProcessError as err:
            print err.message
            print ('Unable to merge files in gdal_processing._create_layerstacks(). Exiting')
            raise IOError

    def _process_layerstacks(self, dataset_info):
        """
        Delegate complex QA processing to DatasetInfo object while providing it with filenames for various stages.
        :param dataset_info: Initialised class for data manipulation
        :return: no return
        """
        dataset_info.initialise_refl(self.m_sdr.get_refl_filename)
        dataset_info.read_QA(self.m_sdr.get_QA_filename)
        dataset_info.screen_using_QA(self.m_sdr.get_layer_filename())

    def _calculate_kernels(self, dataset_info):
        """
        Delegate complex kernel processing to DatasetInfo object while providing it with filenames for various stages.
        :param dataset_info: Initialised class for data manipulation
        :return: no return
        """
        dataset_info.initialise_kernels(self.m_sdr.get_agl_filename())
        dataset_info.calculate_kernels(self.m_sdr.get_layer_kernels_filename())

    def _move_results(self, temp_dir, doy):
        """
        Rename temporary processing files and store in user configured location
        :param temp_dir: working directory
        :param doy: DoY which has been processed
        :return: no return
        """
        os.chdir(temp_dir)
        # move results into central VRTs folder: shutil.move preferred over os.rename
        # mv $TMPDIR/SDS_layerstack_masked.tif $OUTDIR/$product.$year$strDoY.$tile.tif
        # mv $TMPDIR/SDS_layerstack_kernels_masked.tif $OUTDIR/$product.$year$strDoY.$tile.kernels.tif
        if os.path.exists(self.m_sdr.get_layer_filename()):
            shutil.move(self.m_sdr.get_layer_filename(),
                        self.m_config.get_gdal_dir() + self.m_config.get_product() + '.'
                        + str(self.m_config.get_year()) + str(doy) + '.'
                        + self.m_config.get_tile() + '.tif')
        else:
            pass
        if os.path.exists(self.m_sdr.get_layer_kernels_filename()):
            shutil.move(self.m_sdr.get_layer_kernels_filename(),
                        self.m_config.get_gdal_dir() + self.m_config.get_product() + '.'
                        + str(self.m_config.get_year()) + str(doy) + '.'
                        + self.m_config.get_tile() + '.kernels.tif')
        else:
            pass

        # remove the temporary files and process' directory
        os.chdir('..')
        shutil.rmtree(temp_dir)