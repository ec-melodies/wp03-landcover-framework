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

def GetDimensions(File):
    dataset = gdal.Open(File, GA_ReadOnly)
    rows, cols, NumberOfBands = dataset.RasterYSize, dataset.RasterXSize, dataset.RasterCount
    dataset = None

    return rows, cols, NumberOfBands

def WeightSamples( lc_map, lc_fraction = 1., PercentOfSamplesToKeep = 1. ):

    indices = np.where ( lc_map >= lc_fraction )

    if PercentOfSamplesToKeep < 1.:
        r_indices = np.random.randint( 0, high = indices[0].shape[0],
                  size = int( indices[0].shape[0] ) * PercentOfSamplesToKeep )

        indices = ( indices[0][r_indices], indices[1][r_indices] )

    return indices

LC_fraction_fname = sys.argv[1]
statsFile = sys.argv[2]

rows, cols, NumberOfBands = GetDimensions( LC_fraction_fname )
dataset = gdal.Open( LC_fraction_fname , GA_ReadOnly )
LC_fraction = dataset.ReadAsArray()
# Get pixel size (should be a squared pixel and size in meters)
geoTransform = dataset.GetGeoTransform()
pixelSize = geoTransform[1]

del ( dataset )

# From the stats file extract class number and proportion
Stats = np.loadtxt( statsFile )

# Get land cover classes
classes = Stats[:,0].astype(int)
# Class proportion
proportion = Stats[:,2]

numberOfClasses = classes.shape[0]

# Number of pure pixels ( fraction = 1 ) per class
NumberPurePixels = np.zeros((numberOfClasses), np.uint16)

# Create LC samples map
Samples = np.zeros((rows,cols), np.uint16)

for i, lc_class in enumerate( classes ):
    # For some udersampled clasess apply a lenient threshold
    # WeightSamples( LandCover, lc_fraction, PercentOfSamplesToKeep )
    if lc_class == 1 :
        indices = WeightSamples( LC_fraction[i], 0.95, 1. )

    elif lc_class == 2 :
        indices = WeightSamples( LC_fraction[i], 1., 0.18 )

    elif lc_class == 3 :
        indices = WeightSamples( LC_fraction[i], 1., 0.18 )

    #elif lc_class == 4 :
    #    indices = WeightSamples( LC_fraction[i], 1., 1. )

    #elif lc_class == 5 :
    #    indices = WeightSamples( LC_fraction[i], 0.98, 1. )

    elif lc_class == 6 :
        indices = WeightSamples( LC_fraction[i], 0.85, 1. )

    elif lc_class == 7 :
        indices = WeightSamples( LC_fraction[i], 1., 0.1 )

    elif lc_class == 8 :
        indices = WeightSamples( LC_fraction[i], 1., 0.18 )

    elif lc_class == 9 :
        indices = WeightSamples( LC_fraction[i], 0.95, 1. )

    elif lc_class == 10 :
        indices = WeightSamples( LC_fraction[i], 1., 0.45 )

    elif lc_class == 11 :
        indices = WeightSamples( LC_fraction[i], 1., 0.3 )

    elif lc_class == 12 :
        indices = WeightSamples( LC_fraction[i], 1., 0.09 )

    elif lc_class == 13 :
        indices = WeightSamples( LC_fraction[i], 1., 0.04 )

    elif lc_class == 15 :
        indices = WeightSamples( LC_fraction[i], 1., 0.04 )

    elif lc_class == 16 :
        indices = WeightSamples( LC_fraction[i], 1., 0.11 )

    elif lc_class == 17 :
        indices = WeightSamples( LC_fraction[i], 1., 0.1 )

    elif lc_class == 18 :
        indices = WeightSamples( LC_fraction[i], 1., 0.1 )

    elif lc_class == 19 :
        indices = WeightSamples( LC_fraction[i], 1., 0.05 )

    elif lc_class == 20 :
        indices = WeightSamples( LC_fraction[i], 1., 0.05 )

    elif lc_class == 21 :
        indices = WeightSamples( LC_fraction[i], 1., 0.25 )    

    elif lc_class == 22 :
        indices = WeightSamples( LC_fraction[i], 0.98, 1. )

    else:
        indices = WeightSamples( LC_fraction[i], 1., 1. )

    # Get the total number of pure/representative pixels per class
    Samples[ indices[0], indices[1] ] = lc_class
    NumberPurePixels[i] = indices[0].shape[0]

TotalNumberPurePixels = NumberPurePixels.sum().astype(float)

for i, lc_class in enumerate( classes ):
    print lc_class, proportion[i], NumberPurePixels[i] / TotalNumberPurePixels, NumberPurePixels[i]

print "Writing results to a file..."
format = "ENVI"
driver = gdal.GetDriverByName(format)

new_dataset = driver.Create('SamplesFromFractions.img', cols, rows, 1, GDT_UInt16)
new_dataset.GetRasterBand(1).WriteArray(Samples[:,:])
new_dataset = None

