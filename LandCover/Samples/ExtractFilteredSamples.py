#!/usr/bin/env python

try:
    import osgeo.gdal as gdal
    from osgeo.gdalconst import *
    gdal.UseExceptions()
except ImportError:
    print 'GDAL is not installed.'
    exit(-1)

try:
    import numpy as np
except ImportError:
    print 'NumPy is not installed.'
    exit(-1)

import sys

from IPython import embed
from pylab import *

def GetDimensions(File):
    dataset = gdal.Open(File, GA_ReadOnly)
    rows, cols, NumberOfBands = dataset.RasterYSize, dataset.RasterXSize, dataset.RasterCount
    dataset = None

    return rows, cols, NumberOfBands

samples_mean_fname = sys.argv[1]
samples_std_fname = sys.argv[2]
samples_fname = sys.argv[3]
samples_stats = sys.argv[4]

# Statistics from original samples
SampleStats = np.loadtxt( samples_stats )
LC_classes = SampleStats[:,0].astype(np.int8)

# Get samples statistics
samples_refl_mean = np.loadtxt( samples_mean_fname )
samples_refl_std  = np.loadtxt( samples_std_fname )

# Load reflectance data
# Surface reflectance data
datadir = "/home/dn907640/MELODIES/data/MODIS/processing/mosaics/2007/interpolated"
b1 = gdal.Open( datadir + '/2007.only.f0.b1.interpolated.vrt').ReadAsArray()
b2 = gdal.Open( datadir + '/2007.only.f0.b2.interpolated.vrt').ReadAsArray()
b7 = gdal.Open( datadir + '/2007.only.f0.b7.interpolated.vrt').ReadAsArray()

rows, cols, NumberOfBands = GetDimensions( samples_fname )
dataset = gdal.Open( samples_fname , GA_ReadOnly )
# Get pixel size (should be a squared pixel and size in meters)
geoTransform = dataset.GetGeoTransform()
pixelSize = geoTransform[1]
samples = dataset.ReadAsArray()
dataset = None

# Extract per band/class spectral statistics
bands = np.array([1,2,7])
band_names = ['Red', 'NIR', 'SWIR']

NumSD = 1
ValidObsPct = 75

for LC_class in LC_classes:
#for LC_class in [1]:
    #figure()

    if LC_class == 1: # iBradleave Woodland
        classSD = NumSD
        classValidObsPct = 80
    elif LC_class == 3: # Arable and Horticulture
        classSD = NumSD + 0.5
        classValidObsPct = 80
    elif LC_class == 4: # Improved Grassland
        classSD = NumSD + 0.5
        classValidObsPct = 80
    elif LC_class == 9: # Fen, Marsh and Swamp
        classSD = NumSD + 0.5
        classValidObsPct = 80
    elif LC_class == 11: # Heather Glassland
        classSD = NumSD + 0.1
        classValidObsPct = 80
    elif LC_class == 12: # Bog
        classSD = NumSD - 0.2
        classValidObsPct = 80
    elif LC_class == 13: # Montane habitats
        classSD = NumSD - 0.3
        classValidObsPct = 80
    elif LC_class == 15: # Saltwater
        classSD = NumSD - 0.3
        classValidObsPct = 80
    elif LC_class == 16: # Freshwater
        classSD = NumSD - 0.2
        classValidObsPct = 80
    elif LC_class == 14: # Montane habitats
        classSD = NumSD - 0.25
        classValidObsPct = 80
    elif LC_class == 17: # supra litoral rock
        classSD = NumSD + 0.5
        classValidObsPct = 80
    elif LC_class == 20: # Littoral sediment
        classSD = NumSD - 0.3
        classValidObsPct = 80
    else:
        classSD = NumSD

    #classSD = NumSD

    for band in bands:
        band_indices = np.where( samples_refl_mean[:,1] == band )
        band_mean = samples_refl_mean[band_indices]
        band_std = samples_refl_std[band_indices]

        class_indices = np.where( band_mean[:,0] == LC_class )

        profile_refl_mean = band_mean[ class_indices[0][0], 2:]
        profile_refl_std = band_std[ class_indices[0][0], 2:]

        #errorbar ( range( profile_refl_mean.shape[0] ),
        #       profile_refl_mean,
        #       profile_refl_std )

        # Filter samples
        indices = np.where( samples == LC_class )
        tmp_band = eval( 'b' + str(band))
        for i in range( indices[0].shape[0] ):
            profile = tmp_band[ :, indices[0][i], indices[1][i] ]

            upper_boundary = ( profile >= ( profile_refl_mean - ( profile_refl_std * classSD ) ) )
            lower_boundary = ( profile <= ( profile_refl_mean + ( profile_refl_std * classSD ) ) )
            obs_within_boundaries_count = ( upper_boundary * lower_boundary ).sum()

            if obs_within_boundaries_count < int( profile.shape[0] * ( ValidObsPct / 100. ) ):
                samples[ indices[0][i], indices[1][i] ] = 0

            # Check for outliers - values outside 3 standard deviations
            upper_boundary = ( profile >= ( profile_refl_mean - ( profile_refl_std * 3 ) ) )
            lower_boundary = ( profile <= ( profile_refl_mean + ( profile_refl_std * 3 ) ) )
            obs_within_boundaries_count = ( upper_boundary * lower_boundary ).sum()

            if obs_within_boundaries_count < profile.shape[0] :
                samples[ indices[0][i], indices[1][i] ] = 0


#ipshell = embed()

'''
for band in bands:
    figure()

    band_indices = np.where( samples_refl_mean[:,1] == band )
    band_mean = samples_refl_mean[band_indices]
    band_std = samples_refl_std[band_indices]

    #for LC_class in LC_classes:
    for LC_class in [3,4]:
        class_indices = np.where( band_mean[:,0] == LC_class )

        profile_refl_mean = band_mean[ class_indices[0][0], 2:]
        profile_refl_std = band_std[ class_indices[0][0], 2:]

        errorbar ( range( profile_refl_mean.shape[0] ),
               profile_refl_mean,
               profile_refl_std )

    ipshell = embed()
'''


print "Writing results to a file..."
format = "ENVI"
driver = gdal.GetDriverByName(format)

fname = "FilteredSamples." + "SD_" + str(NumSD) + ".ValidObsPct_" + str(ValidObsPct) + ".img"
new_dataset = driver.Create(fname, cols, rows, 1, GDT_UInt16)
new_dataset.GetRasterBand(1).WriteArray( samples[:,:] )
new_dataset = None

