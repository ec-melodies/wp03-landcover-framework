__author__ = 'Jane'

# Class:

class SciDataRecords:
# set up scientific data records, getters for pixel size and other bits
    def __init__(self):
        # Scientific Data Records to extract
        m_sds_type = "HDF4_EOS:EOS_GRID"
        m_sdr = ("MODIS_Grid_1km_2D:state_1km_1",
                 "MODIS_Grid_1km_2D:SensorZenith_1", "MODIS_Grid_1km_2D:SensorAzimuth_1",
                 "MODIS_Grid_1km_2D:SolarZenith_1", "MODIS_Grid_1km_2D:SolarAzimuth_1",
                 "MODIS_Grid_500m_2D:sur_refl_b01_1", "MODIS_Grid_500m_2D:sur_refl_b02_1",
                 "MODIS_Grid_500m_2D:sur_refl_b03_1", "MODIS_Grid_500m_2D:sur_refl_b04_1",
                 "MODIS_Grid_500m_2D:sur_refl_b05_1", "MODIS_Grid_500m_2D:sur_refl_b06_1",
                 "MODIS_Grid_500m_2D:sur_refl_b07_1")

        m_num_sdr = len(self.m_sdr)
        m_lookup = {}

        self._create_lookup()

    def _create_lookup(self):
        for item in self.m_sdr:
            size = str(item).split(':')[0].split('_')[2]
            filename = str(item).split(':')[1] + '.vrt'
            self.m_lookup[item] = (size, filename)

    def get_sds_type(self):
        return self.m_sds_type

    def get_num_sdrs(self):
        return self.m_num_sdr

    def get_sdr(self, index):
        return self.m_sdr[index]

    def lookup_sdr_details(self, index):
        key = self.m_sdr[index]
        return (self.m_lookup[key][0], self.m_lookup[key][1])

    def get_gdalmerge_filenames(self):
        return ('sur_refl', 'Zenith', 'Azimuth')
