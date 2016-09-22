__author__ = 'Jane'
import shutil
import os
import glob
import sys

import nose.tools as ns
import filecmp
from multiprocessing import Queue
import subprocess
from ProcessMOD.src.processMODISdata import main, create_parser
from modis_config.src.configuration import Configuration
from modis_config.src.constants import defs as constants
import GetData.src.getData as get_data
import ProcessMOD.src.sci_data_records as sdrs
import ProcessMOD.src.gdal_processing as g_proc
import gdal_vrtmerge as gmerge

# ensure the file system is clear of test and intermediate files/folders
def clean_up():
    try:
        for dr in glob.glob('.\data*'):
            os.chmod(dr, 0777)
            shutil.rmtree(dr, ignore_errors=True)
        for dr in glob.glob(os.path.expanduser('~') + '\data'):
            os.chmod(dr, 0777)
            shutil.rmtree(dr, ignore_errors=True)
        for dr in glob.glob('.\gdal_files'):
            shutil.rmtree(dr, ignore_errors=True)
        for fl in glob.glob('.\scrape.txt'):
            os.remove(fl)
    except Exception as ex:
        raise ex

def get_data_to_manipulate():
    if get_data.is_website_live():
        # download files for DoY 362, 363, and 364 - only first 1000 bytes
        args = get_data.create_parser(['-file', 'land_cover_config_test.ini', '-test', 'Real'])
        get_data.main(args)
    else:
        ns.assert_true(False, msg="Website down, unable to run test")

def set_up_config(mode, the_file):
    config = Configuration()
    config.read_config(mode, the_file)
    return config

# Test the SciDataRecord class
def test_sci_data_record_number():
    sdr = sdrs.SciDataRecords()
    ns.assert_equals(sdr.get_num_sdrs(), 12)

def test_sci_data_record_lookup_0():
    sdr = sdrs.SciDataRecords()
    the_sdr = sdr.lookup_sdr_details(0)
    ns.assert_tuple_equal(('1km', 'state_1km_1.vrt'), the_sdr)

def test_sci_data_record_lookup_5():
    sdr = sdrs.SciDataRecords()
    the_sdr = sdr.lookup_sdr_details(5)
    ns.assert_tuple_equal(('500m', 'sur_refl_b01_1.vrt'), the_sdr)

def test_sci_data_merge_filenames():
    sdr = sdrs.SciDataRecords()
    ns.assert_equal(sdr.get_gdalmerge_filenames()[sdrs.File_index.Zenith], 'Zenith')

@ns.with_setup(setup=get_data_to_manipulate, teardown=clean_up)
def test_success_default_ini_file():
    args = create_parser(['-test'])
    ns.assert_is_none(main(args))

# Test the gdal processing methods
def test_gdal_default_folder():
    cfg = set_up_config(1, constants['file'])   # process mode
    expected_folder = os.path.expanduser('~') + '\data\h18v04\MOD09GA' + os.path.sep + 'VRTs' + os.path.sep
    ns.assert_equals(cfg.get_gdal_dir(), expected_folder)

def test_gdal_prcs_section_folder():
    cfg = set_up_config(1, 'land_cover_config_test_gdal.ini')   # process mode
    expected_folder = os.getcwd() + os.path.sep + '.\gdal_files' + os.path.sep
    ns.assert_equals(cfg.get_gdal_dir(), expected_folder)

@ns.raises(SystemExit)
@ns.with_setup(setup=get_data_to_manipulate, teardown=clean_up)
def test_gdal_processing_year():
    # get days 362, 363, and 364 in year 2007 using get_data_to_manipulate()
    # but set year to process as 2006
    args = create_parser(['-file', 'land_cover_config_test_year.ini', '-test'])
    main(args)

@ns.raises(SystemExit)
@ns.with_setup(setup=get_data_to_manipulate, teardown=clean_up)
def test_gdal_processing_days():
    # get days 362, 363, and 364 in year 2007 using get_data_to_manipulate()
    # but set days to process as 100 to 110
    args = create_parser(['-file', 'land_cover_config_test_days.ini', '-test'])
    main(args)

@ns.with_setup(setup=get_data_to_manipulate, teardown=clean_up)
def test_gdal_processing_queue():
    # get days 362, 363, and 364 using get_data_to_manipulate()
    # process days 362 to 365 (which latter is default when no DoYend is set)
    cfg = set_up_config(1, 'land_cover_config_test_gdal.ini')   # process mode
    # create expected queue
    expected_q = Queue()
    # use config to get target filenames and doy range
    for day in range(cfg.get_doy_range()[0], cfg.get_doy_range()[1] + 1):
        hdf_file, xml_file = cfg.create_local_filenames()
        cfg.next_day()
        # check file exists before adding to queue
        if os.path.exists(hdf_file):
            # each q item is list of path & doy
            q_item = (hdf_file, day)
            expected_q.put(q_item)

    proc = g_proc.GdalProcessing()
    proc.set_config_object(cfg)
    the_queue = proc._distribute_gdal_work(testing=True)
    while not expected_q.empty():
        expected_item = expected_q.get()
        the_item = the_queue.get()
        ns.assert_tuple_equal(the_item, expected_item)

@ns.with_setup(setup=get_data_to_manipulate, teardown=clean_up)
def test_gdal_do_work():
    # this does chdir to subprocess: remains in that dir for next tests so fails on next but one test where needs config
    test_dir = os.getcwd()
    # get days 362, 363, and 364 using get_data_to_manipulate()
    # process days 362 to 365 (which latter is default when no DoYend is set)
    cfg = set_up_config(1, 'land_cover_config_test_gdal.ini')   # process mode
    # create expected queue - only need one item this time
    q = Queue()
    # use config to get target filename and doy
    day = cfg.get_doy_range()[0]
    hdf_file, xml_file = cfg.create_local_filenames()
    if os.path.exists(hdf_file):
        q_item = (hdf_file, day)
        q.put(q_item)
    proc = g_proc.GdalProcessing()
    proc.set_config_object(cfg)
    result_dir, results = proc._do_work(q, testing=True)
    os.chdir(test_dir)
    ns.assert_true(filecmp.cmp(result_dir + os.path.sep + results, test_dir + os.path.sep + 'gdal_do_work_reference.txt'))

@ns.raises(IOError)
def test_gdal_create_layerstacks():
    # this test raises the system exit as there are no files to process
    proc = g_proc.GdalProcessing()
    cfg = set_up_config(1, 'land_cover_config_test_gdal.ini')   # process mode
    proc.set_config_object(cfg)
    proc._create_layerstacks(os.getcwd())

@ns.with_setup(teardown=clean_up)
def test_gdal_move_results():
    proc = g_proc.GdalProcessing()
    cfg = set_up_config(1, 'land_cover_config_test_gdal.ini')   # process mode
    sdr = sdrs.SciDataRecords()
    proc.set_config_object(cfg)
    # create the files
    temp_dir = os.getcwd() + os.path.sep + 'move_test' + os.path.sep
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    os.chdir(temp_dir)
    open(sdr.get_layer_filename(), 'w')
    open(sdr.get_layer_kernels_filename(), 'w')
    # move/rename them
    dest = cfg.get_gdal_dir()
    proc._move_results(temp_dir, 100)    # 100 is a made up DoY
    # the file names are created from the values in the ini file
    ns.assert_true(os.path.exists('.' + os.path.sep + 'gdal_files' + os.path.sep + 'MOD09GA.2007100.h18v04.tif'))
    ns.assert_true(os.path.exists('.' + os.path.sep + 'gdal_files' + os.path.sep + 'MOD09GA.2007100.h18v04.kernels.tif'))
    ns.assert_false(os.path.exists('.' + os.path.sep + 'move_test' + os.path.sep))

# Test the dataset class
# TODO This requires some detailed test data and considerable effort


