__author__ = 'Jane'

import os
try:
    import numpy as np
except ImportError:
    print 'Numpy is not installed.'
    exit(-1)
try:
    import osgeo.gdal as gdal
    from osgeo.gdalconst import *
    gdal.UseExceptions()
except ImportError:
    print 'GDAL is not installed.'
    exit(-1)

import Kernels as knl

class DatasetInfo:
    """
    Class to do image processing.

    Methods defined here:
        initialise_refl(...)
            Retrieve basic dataset info and set up 3D array to hold reflectance bands.

        read_QA(...)
            Open the quality file and retrieve its data.

        screen_using_QA(...)
            Create a new dataset by applying quality parameters.

        initialise_kernels(...)
            Retrieve basic dataset info and set up 3D array to hold angular data.

        calculate_kernels(...)
            Calculate angular data.

    ----------------------------------------------------------------------
    No data or other attributes defined here.
    """
    def __init__(self, folder):
        self.m_folder = folder
        self.m_rows = 0
        self.m_cols = 0
        self.m_number_of_bands = 0

        self.m_projection = None
        self.m_geo_transform = None

        self.m_uncert = None
        self.m_layerstack = None
        self.m_QA = None

        self.m_cloud = None
        self.m_cloudshadow = None
        self.m_land_water = None
        self.m_internal_cloud_flag = None
        self.m_snow_ice_flag = None
        self.m_pixel_adjacent_to_cloud = None
        self.m_aerosols_QA = None
        self.m_refl_SD_noise_estimates = {1:0.004, 2:0.015, 3:0.003, 4:0.004, 5:0.013, 6:0.010, 7:0.006 }
        self.m_refl_scale_factor = 10000.

        self.m_angles = None

    def _init_base(self, filename):
        """
        Set the working directory, open the file and retrieve basic information.

        :param filename: input file containing dataset
        :return: opened GDAL dataset
        """
        os.chdir(self.m_folder)
        dataset = gdal.Open(filename, GA_ReadOnly )
        self.m_rows = dataset.RasterYSize
        self.m_cols = dataset.RasterXSize
        self.m_number_of_bands = dataset.RasterCount
        return dataset

    def initialise_kernels(self, filename):
        """
        Retrieve basic dataset info and set up 3D array to hold angular data.

        :param filename: input file containing dataset
        :return: no return
        """
        AnglesScalingFactor = 100.
        dataset = self._init_base(filename)
        self.m_angles = np.zeros((self.m_rows, self.m_cols, self.m_number_of_bands), np.float32)
        print "Reading angular bands..."
        for i in range(self.m_number_of_bands):
            self.m_angles[:, :, i] = dataset.GetRasterBand(i+1).ReadAsArray() / AnglesScalingFactor

    def initialise_refl(self, filename):
        """
        Retrieve basic dataset info and set up 3D array to hold reflectance bands.

        :param filename: input file containing dataset
        :return: no return
        """
        dataset = self._init_base(filename)
        # Get projection information
        self.m_projection = dataset.GetProjection()
        self.m_geo_transform = dataset.GetGeoTransform()
        # Layerstack for reflectances uncertainty
        self.m_uncert = np.zeros((self.m_rows, self.m_cols, self.m_number_of_bands), np.int16)

        # Layerstack for reflectances
        self.m_layerstack = np.zeros((self.m_rows, self.m_cols, self.m_number_of_bands), np.int16)
        print "Reading refl bands..."
        for i in range(self.m_number_of_bands):
            self.m_layerstack[:,:,i] = dataset.GetRasterBand(i+1).ReadAsArray()

    def read_QA(self, QAfilename):
        """
        Open the quality file and retrieve its data.
        :param QAfilename: input file containing QA dataset
        :return:
        """
        dataset = gdal.Open(QAfilename)
        self.m_QA = dataset.GetRasterBand(1).ReadAsArray()

        self._setupQAinfo()

    def screen_using_QA(self, dataset_filename):
        """
        Create a new dataset by applying quality parameters.

        :param dataset_filename: opened GDAL dataset
        :return: no return
        """
        # save masked reflectance to a geoTiff file... create it first
        gtiff_format = "GTiff"
        driver = gdal.GetDriverByName(gtiff_format)
        # Seven spectral bands plus uncertainty and snow mask
        new_dataset = driver.Create(dataset_filename, self.m_cols, self.m_rows,
                                    (self.m_number_of_bands * 2) + 1, GDT_Int16,
                                    ['COMPRESS=PACKBITS'])

        for i in range(self.m_number_of_bands):
            self.m_layerstack[:, :, i] = self.m_layerstack[:, :, i] * self.m_cloud \
                                         * self.m_cloudshadow * self.m_land_water \
                                         * self.m_internal_cloud_flag * self.m_pixel_adjacent_to_cloud

            self.m_layerstack[:, :, i] = np.where((self.m_layerstack[:, :, i] < 0) |
                                                  (self.m_layerstack[:, :, i] > self.m_refl_scale_factor),
                                                  0, self.m_layerstack[:, :, i])

            new_dataset.GetRasterBand(i + 1).WriteArray(self.m_layerstack[:, :, i])

            self.m_uncert[:, :, i] = (((self.m_layerstack[:, :, i] / self.m_refl_scale_factor)
                                       * self.m_aerosols_QA) + (self.m_refl_SD_noise_estimates[i + 1])) \
                                       * self.m_refl_scale_factor

            self.m_uncert[:, :, i] = self.m_uncert[:,:,i] * self.m_cloud \
                                     * self.m_cloudshadow * self.m_land_water \
                                     * self.m_internal_cloud_flag * self.m_pixel_adjacent_to_cloud

            self.m_uncert[:, : ,i] = np.where((self.m_uncert[:, :, i] < 0) |
                                              (self.m_uncert[:, :, i] > self.m_refl_scale_factor),
                                              0, self.m_uncert[:,:,i])

            new_dataset.GetRasterBand(i + 1 + self.m_number_of_bands).WriteArray(self.m_uncert[:, :, i])

        snow_mask = self.m_snow_ice_flag * self.m_cloud * self.m_cloudshadow \
                    * self.m_land_water * self.m_internal_cloud_flag * self.m_pixel_adjacent_to_cloud
        new_dataset.GetRasterBand((self.m_number_of_bands * 2) + 1).WriteArray(snow_mask)

        new_dataset.SetProjection(self.m_projection)
        new_dataset.SetGeoTransform(self.m_geo_transform)

    def _setupQAinfo(self):
        """
        Use the quality file to populate arrays affecting reflectance readings.
        :return: no return
        """
        # QA information for MOD09GA
        # https://lpdaac.usgs.gov/products/modis_products_table/mod09ga
        print "Masking data..."
        # Bit 0-1 cloud state: 00 - clear
        bit0, bit1 = 0, 1
        self.m_cloud = np.where(((self.m_QA / np.power(2,bit0)) % 2 == 0) &
                                ((self.m_QA / np.power(2,bit1)) % 2 == 0), 1, 0)

        # Bit 2 cloud shadow: 0 - no cloud shadow
        bit2 = 2
        self.m_cloudshadow = np.where( (self.m_QA / np.power(2,bit2)) % 2 == 0, 1, 0)

        # Bits 3-5 land-water flag
        # 000 - shallow ocean
        # 110 - continental/moderate ocean
        # 111 - deep ocean
        bit3 = 3
        bit4 = 4
        bit5 = 5

        self.m_land_water = np.where(((self.m_QA / np.power(2,bit3)) % 2 == 0) &
                             ((self.m_QA / np.power(2,bit4)) % 2 == 0) &
                             ((self.m_QA / np.power(2,bit5)) % 2 == 0), 0, 1)

        self.m_land_water = np.where(((self.m_QA / np.power(2,bit3)) % 2 == 0) &
                             ((self.m_QA / np.power(2,bit4)) % 2 == 1) &
                             ((self.m_QA / np.power(2,bit5)) % 2 == 1), 0, self.m_land_water)

        self.m_land_water = np.where(((self.m_QA / np.power(2,bit3)) % 2 == 1) &
                             ((self.m_QA / np.power(2,bit4)) % 2 == 1) &
                             ((self.m_QA / np.power(2,bit5)) % 2 == 1), 0, self.m_land_water)

        # Bit 10  internal cloud flag: 0 - no cloud
        bit10 = 10
        self.m_internal_cloud_flag = np.where((self.m_QA / np.power(2,bit10)) % 2 == 0, 1, 0)

        # Bit 12 MOD35 snow/ice flag: 1 - snow
        bit12 = 12
        self.m_snow_ice_flag = np.where( (self.m_QA / np.power(2,bit12)) % 2 == 1, 1, 0)

        # Bit 13 Pixel is adjacent to cloud : 0 - no
        bit13 = 13
        self.m_pixel_adjacent_to_cloud = np.where( (self.m_QA / np.power(2,bit13)) % 2 == 0, 1, 0)

        # Set uncertainty based aerosol QA
        # Bit 6-7 Aerosol quantity:
        # 00 - climatology
        # 01 - low
        # 10 - average
        # 11 - high
        aerosols = {1: 0.01, 2: 0.02, 3: 0.03, 4: 0.04}
        bit6, bit7 = 6, 7

        # UncerntAOD = np.array(4, np.float32)
        self.m_aerosols_QA = np.zeros((self.m_rows, self.m_cols), np.float32)
        self.m_aerosols_QA = np.where(((self.m_QA / np.power(2, bit6)) % 2 == 0)
                                      & ((self.m_QA / np.power(2, bit7)) % 2 == 0),
                                      aerosols[1], self.m_aerosols_QA)
        self.m_aerosols_QA = np.where(((self.m_QA / np.power(2,bit6)) % 2 == 0)
                                      & ((self.m_QA / np.power(2, bit7)) % 2 == 1),
                                      aerosols[2], self.m_aerosols_QA)
        self.m_aerosols_QA = np.where(((self.m_QA / np.power(2,bit6)) % 2 == 1)
                                      & ((self.m_QA / np.power(2, bit7)) % 2 == 0),
                                      aerosols[3], self.m_aerosols_QA)
        self.m_aerosols_QA = np.where(((self.m_QA / np.power(2,bit6)) % 2 == 1)
                                      & ((self.m_QA / np.power(2, bit7)) % 2 == 1),
                                      aerosols[4], self.m_aerosols_QA)

    def calculate_kernels(self, dataset_filename):
        """
        Calculate angular data.
        :param dataset_filename: opened GDAL dataset
        :return: no return
        """
        VZA, SZA, VAA, SAA = self.m_angles[:, :, 0], self.m_angles[:, :, 1],\
                             self.m_angles[:, :, 2], self.m_angles[:, :, 3],

        # Calculate Relative Azimuth Angle as
        # Solar azimuth minus viewing azimuth
        RAA = SAA - VAA

        # Kernels receives vza, sza, raa
        print 'Calculating Ross-Thick and Li-Sparse kernels...'
        kk = knl.Kernels(VZA, SZA, RAA,
                         RossHS=False, RecipFlag=True, MODISSPARSE=True,
                         normalise=1, doIntegrals=False, LiType='Sparse', RossType='Thick')

        Ross_Thick = np.zeros((self.m_rows, self.m_cols), np.float32)
        Li_Sparse = np.zeros((self.m_rows, self.m_cols), np.float32)

        Ross_Thick = kk.Ross.reshape((self.m_rows, self.m_cols))
        Ross_Thick = Ross_Thick * self.m_cloud * self.m_cloudshadow * \
                     self.m_land_water * self.m_internal_cloud_flag * \
                     self.m_pixel_adjacent_to_cloud

        Li_Sparse = kk.Li.reshape((self.m_rows, self.m_cols))
        Li_Sparse = Li_Sparse * self.m_cloud * self.m_cloudshadow * \
                    self.m_land_water * self.m_internal_cloud_flag * \
                    self.m_pixel_adjacent_to_cloud

        # Save kernels in a different file to keep all 32bit floating point information
        gtiff_format = "GTiff"
        driver = gdal.GetDriverByName(gtiff_format)
        new_dataset = driver.Create(dataset_filename, self.m_rows, self.m_cols, 2, GDT_Float32, ['COMPRESS=PACKBITS'] )
        new_dataset.GetRasterBand(1).WriteArray(Ross_Thick)
        new_dataset.GetRasterBand(2).WriteArray(Li_Sparse)

