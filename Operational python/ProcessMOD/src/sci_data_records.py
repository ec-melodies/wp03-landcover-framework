__author__ = 'Jane'

"""
Enumeration to index into filename array
"""
def enum(**enums):
    return type('Enum', (), enums)

File_index = enum(sur_refl=0, Zenith=1, Azimuth=2)

class SciDataRecords:
    """
    Class to hold data record and file identification.

    Methods defined here:
        get_sds_type(...)
            Get the Scientific Data type

        get_num_sdrs(...)
            Get the number of scientific data record names

        get_sdr(...)
            Get specific scientific data record name

        lookup_sdr_details(...)
            Get the scale and vrt file name for specific record

        get_gdalmerge_filenames(...)
            Get the names of the three types of vrt file for GDAL merging.

        get_QA_filename(...)
            Get the temporary name for the QA file

        get_refl_filename(...)
            Get the temporary name for the reflectance file

        get_agl_filename(...)
            Get the temporary name for the angles file

        get_layer_filename(...)
            Get the temporary name for the layerstack file

        get_layer_kernels_filename(...)
            Get the temporary name for the layerstack kernels file

    """

    def __init__(self):
        # Scientific Data Records to extract
        self.m_sds_type = "HDF4_EOS:EOS_GRID"
        self.m_sdr = ("MODIS_Grid_1km_2D:state_1km_1",
                      "MODIS_Grid_1km_2D:SensorZenith_1", "MODIS_Grid_1km_2D:SensorAzimuth_1",
                      "MODIS_Grid_1km_2D:SolarZenith_1", "MODIS_Grid_1km_2D:SolarAzimuth_1",
                      "MODIS_Grid_500m_2D:sur_refl_b01_1", "MODIS_Grid_500m_2D:sur_refl_b02_1",
                      "MODIS_Grid_500m_2D:sur_refl_b03_1", "MODIS_Grid_500m_2D:sur_refl_b04_1",
                      "MODIS_Grid_500m_2D:sur_refl_b05_1", "MODIS_Grid_500m_2D:sur_refl_b06_1",
                      "MODIS_Grid_500m_2D:sur_refl_b07_1")

        self.m_num_sdr = len(self.m_sdr)

        self.m_lookup = {}
        self._create_lookup()

        # temporary working file names
        self.m_QA_filename = 'state_1km_1.vrt'
        self.m_reflectance_filename = 'sur_refl.vrt'
        self.m_angles_filename = 'angles.vrt'
        self.m_layer_filename = 'SDS_layerstack_masked.tif'
        self.m_layer_kernels_filename = 'SDS_layerstack_kernels_masked.tif'

    def _create_lookup(self):
        """
        Split the SDR name to extract the scale (3rd element in first part) and
        the name to be used for the vrt file (second part)
        :return: no return
        """
        for item in self.m_sdr:
            size = str(item).split(':')[0].split('_')[2]
            filename = str(item).split(':')[1] + '.vrt'
            self.m_lookup[item] = (size, filename)

    def get_sds_type(self):
        """
        Get the Scientific Data type
        :return: Scientific Data type
        """
        return self.m_sds_type

    def get_num_sdrs(self):
        """
        Get the number of scientific data record names
        :return: number of scientific data record names
        """
        return self.m_num_sdr

    def get_sdr(self, index):
        """
        Get specific scientific data record name
        :param index: required record
        :return: name of scientific data record
        """
        return self.m_sdr[index]

    def lookup_sdr_details(self, index):
        """
        Get the scale and vrt file name for specific record
        :param index: required record
        :return: tuple containing scale and file name
        """
        key = self.m_sdr[index]
        return self.m_lookup[key][0], self.m_lookup[key][1]

    @staticmethod
    def get_gdalmerge_filenames():
        """
        Get the names of the three types of vrt file for GDAL merging.
        Use the enum index defined above to access them.
        :return: list containing three file names
        """
        # Note that this may look long-winded but it is robust: the list order is controlled only by the enum.
        filenames = [None] * 3
        filenames[File_index.sur_refl] = 'sur_refl'
        filenames[File_index.Zenith] = 'Zenith'
        filenames[File_index.Azimuth] = 'Azimuth'
        return filenames

    def get_QA_filename(self):
        """
        Get the temporary name for the QA file
        :return: name of QA file
        """
        return self.m_QA_filename

    def get_refl_filename(self):
        """
        Get the temporary name for the reflectance file
        :return: name of reflectance file
        """
        return self.m_reflectance_filename

    def get_agl_filename(self):
        """
        Get the temporary name for the angles file
        :return: name of angles file
        """
        return self.m_angles_filename

    def get_layer_filename(self):
        """
        Get the temporary name for the layerstack file
        :return: name of layerstack file
        """
        return self.m_layer_filename

    def get_layer_kernels_filename(self):
        """
        Get the temporary name for the layerstack kernels file
        :return: name of layerstack kernels file
        """
        return self.m_layer_kernels_filename
