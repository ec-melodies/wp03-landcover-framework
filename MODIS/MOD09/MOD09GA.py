# -*- coding: utf-8 -*-

__author__ = "Gerardo López Saldaña"
__version__ = "0.1 (12.05.2014)"
__email__ = "G.LopezSaldana@reading.ac.uk"

import sys

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

from IPython import embed

HomeDir = '/home/dn907640'
Project = 'MELODIES'
sys.path.append(HomeDir + '/' + Project + '/' + 'src/DataHandling')
from DataHandling import *

# Read reflectances layerstack
dataset = gdal.Open( 'sur_refl.vrt', GA_ReadOnly )
rows, cols, NumberOfReflBands = GetDimensions( 'sur_refl.vrt' )

# Get projection information
Projection = dataset.GetProjection()
GeoTransform = dataset.GetGeoTransform()

# Layerstack for reflectances uncert
uncert = np.zeros((rows, cols, NumberOfReflBands), np.int16)

# Layerstack for reflectances
layerstack = np.zeros((rows, cols, NumberOfReflBands), np.int16)
print "Reading refl bands..."
for i in range(NumberOfReflBands):
	layerstack[:,:,i] = dataset.GetRasterBand(i+1).ReadAsArray()

dataset = None

# Read QA information
dataset = gdal.Open( 'state_1km_1.vrt' )
QA = dataset.GetRasterBand(1).ReadAsArray()

# QA information for MOD09GA
# https://lpdaac.usgs.gov/products/modis_products_table/mod09ga
print "Masking data..."
# Bit 0-1 cloud state: 00 - clear
bit0, bit1 = 0, 1
Cloud = np.where( ((QA / np.power(2,bit0)) % 2 == 0) & ((QA / np.power(2,bit1)) % 2 == 0), 1, 0)

# Bit 2 cloud shadow: 0 - no cloud shadow
bit2 = 2
CloudShadow = np.where( (QA / np.power(2,bit2)) % 2 == 0, 1, 0)

# Bits 3-5 land-water flag
# 000 - shallow ocean
# 110 - continental/moderate ocean
# 111 - deep ocean
bit3 = 3
bit4 = 4
bit5 = 5
LandWater =  np.where( ((QA / np.power(2,bit3)) % 2 == 0) & \
                       ((QA / np.power(2,bit4)) % 2 == 0) & \
                       ((QA / np.power(2,bit5)) % 2 == 0) , 0, 1)

LandWater =  np.where( ((QA / np.power(2,bit3)) % 2 == 0) & \
                       ((QA / np.power(2,bit4)) % 2 == 1) & \
                       ((QA / np.power(2,bit5)) % 2 == 1) , 0, LandWater)

LandWater =  np.where( ((QA / np.power(2,bit3)) % 2 == 1) & \
                       ((QA / np.power(2,bit4)) % 2 == 1) & \
                       ((QA / np.power(2,bit5)) % 2 == 1) , 0, LandWater)

# Bit 10  internal cloud flag: 0 - no cloud
bit10 = 10
InternalCloudFlag = np.where( (QA / np.power(2,bit10)) % 2 == 0, 1, 0)

# Bit 12 MOD35 snow/ice flag: 1 - snow
bit12 = 12
SnowIceFlag = np.where( (QA / np.power(2,bit12)) % 2 == 1, 1, 0)

# Bit 13 Pixel is adjacent to cloud : 0 - no
bit13 = 13
PixelAdjacentToCloud = np.where( (QA / np.power(2,bit13)) % 2 == 0, 1, 0)

# Set uncert based aerosol QA
# Bit 6-7 Aerosol quantity:
# 00 - climatology
# 01 - low
# 10 - average
# 11 - high
Aerosols = { 1:0.01, 2:0.02, 3:0.03, 4:0.04 }
bit6, bit7 = 6, 7

UncerntAOD = np.array(4, np.float32)
AerosolsQA = np.zeros((rows, cols), np.float32)
AerosolsQA = np.where( ((QA / np.power(2,bit6)) % 2 == 0) & ((QA / np.power(2,bit7)) % 2 == 0), Aerosols[1], AerosolsQA)
AerosolsQA = np.where( ((QA / np.power(2,bit6)) % 2 == 0) & ((QA / np.power(2,bit7)) % 2 == 1), Aerosols[2], AerosolsQA)
AerosolsQA = np.where( ((QA / np.power(2,bit6)) % 2 == 1) & ((QA / np.power(2,bit7)) % 2 == 0), Aerosols[3], AerosolsQA)
AerosolsQA = np.where( ((QA / np.power(2,bit6)) % 2 == 1) & ((QA / np.power(2,bit7)) % 2 == 1), Aerosols[4], AerosolsQA)

refl_SD_noise_estimates = {1:0.004, 2:0.015, 3:0.003, 4:0.004, 5:0.013, 6:0.010, 7:0.006 }

ReflScaleFactor = 10000.

# Save masked refl to a GeoTiff file
format = "GTiff"
driver = gdal.GetDriverByName(format)
# Seven spectral bands plus uncert and snow mask
new_dataset = driver.Create( 'SDS_layerstack_masked.tif', cols, rows, (NumberOfReflBands * 2) + 1, GDT_Int16 , ['COMPRESS=PACKBITS'])

# Screening using QA
for i in range(NumberOfReflBands):
    layerstack[:,:,i] = layerstack[:,:,i] * Cloud * CloudShadow * LandWater * InternalCloudFlag * PixelAdjacentToCloud
    layerstack[:,:,i] = np.where( (layerstack[:,:,i] < 0) | (layerstack[:,:,i] > ReflScaleFactor), 0, layerstack[:,:,i] )
    new_dataset.GetRasterBand(i + 1).WriteArray(layerstack[:,:,i])

    uncert[:,:,i] = ( ( ( layerstack[:,:,i] / ReflScaleFactor ) * AerosolsQA ) + \
                      ( refl_SD_noise_estimates[i + 1] ) ) * ReflScaleFactor

    uncert[:,:,i] = uncert[:,:,i]  * Cloud * CloudShadow * LandWater * InternalCloudFlag * PixelAdjacentToCloud
    uncert[:,:,i] =  np.where( ( uncert[:,:,i]  < 0) | (uncert[:,:,i] > ReflScaleFactor), 0, uncert[:,:,i] )
    new_dataset.GetRasterBand(i + 1 + NumberOfReflBands).WriteArray(uncert[:,:,i])

SnowMask = SnowIceFlag * Cloud * CloudShadow * LandWater * InternalCloudFlag * PixelAdjacentToCloud
new_dataset.GetRasterBand((NumberOfReflBands * 2) + 1).WriteArray(SnowMask)

new_dataset.SetProjection( Projection )
new_dataset.SetGeoTransform( GeoTransform )

new_dataset = None

# Let's tyde up a bit before calculating the kernels
layerstack = uncert = SnowMask = None

#==================
# Calculate Kernels
#==================
sys.path.append(HomeDir + '/' + Project + '/' + 'src/MODIS/Kernels')
from Kernels import Kernels

AnglesScalingFactor = 100.

# Read angular information layerstack, bands:
# 1 SensorZenith_1.vrt   VZA
# 2 SolarZenith_1.vrt    SZA
# 3 SensorAzimuth_1.vrt  VAA
# 4 SolarAzimuth_1.vrt   SAA

dataset = gdal.Open( 'angles.vrt', GA_ReadOnly )
rows, cols, NumberOfBands = GetDimensions( 'angles.vrt' )

angles = np.zeros((rows, cols, NumberOfBands), np.float32)
print "Reading angular bands..."
for i in range(NumberOfBands):
    angles[:,:,i] = dataset.GetRasterBand(i+1).ReadAsArray() / AnglesScalingFactor

dataset = None

VZA, SZA, VAA, SAA = angles[:,:,0],  angles[:,:,1],  angles[:,:,2],  angles[:,:,3],

# Calculate Relative Azimuth Angle as
# Solar azimuth minus viewing azimuth
RAA = SAA - VAA

# Kernels receives vza, sza, raa
print 'Calculating Ross-Thick and Li-Sparse kernels...'
kk = Kernels(VZA, SZA, RAA, \
             RossHS=False, RecipFlag=True, MODISSPARSE=True, \
             normalise=1, doIntegrals=False, LiType='Sparse', RossType='Thick')

Ross_Thick = np.zeros((rows,cols), np.float32 )
Li_Sparse = np.zeros((rows, cols), np.float32 )

Ross_Thick = kk.Ross.reshape((rows,cols))
Ross_Thick = Ross_Thick * Cloud * CloudShadow * LandWater * InternalCloudFlag * PixelAdjacentToCloud

Li_Sparse = kk.Li.reshape((rows,cols))
Li_Sparse = Li_Sparse * Cloud * CloudShadow * LandWater * InternalCloudFlag * PixelAdjacentToCloud

kk = None

# Save kernels in a different file to keep all 32bit floating point information
new_dataset = driver.Create( 'SDS_layerstack_kernels_masked.tif', cols, rows, 2, GDT_Float32, ['COMPRESS=PACKBITS'] )
new_dataset.GetRasterBand(1).WriteArray(Ross_Thick)
new_dataset.GetRasterBand(2).WriteArray(Li_Sparse)
new_dataset = None


