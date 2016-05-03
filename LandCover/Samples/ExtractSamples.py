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

def GetDimensions(File):
    dataset = gdal.Open(File, GA_ReadOnly)
    rows, cols, NumberOfBands = dataset.RasterYSize, dataset.RasterXSize, dataset.RasterCount
    dataset = None

    return rows, cols, NumberOfBands


mean_LC_fname = sys.argv[1]
mode_LC_fname = sys.argv[2]
statsFile = sys.argv[3]

rows, cols, NumberOfBands = GetDimensions( mean_LC_fname )
dataset = gdal.Open( mean_LC_fname , GA_ReadOnly )
# Get pixel size (should be a squared pixel and size in meters)
geoTransform = dataset.GetGeoTransform()
pixelSize = geoTransform[1]

mean_LC = dataset.GetRasterBand(1).ReadAsArray()
dataset = None

dataset = gdal.Open( mode_LC_fname , GA_ReadOnly )
mode_LC = dataset.GetRasterBand(1).ReadAsArray()
dataset = None

# From the stats file extract class number and proportion
Stats = np.loadtxt( statsFile )

# Get land cover classes
classes = Stats[:,0].astype(int)
# Class proportion
proportion = Stats[:,2]

numberOfClasses = classes.shape[0]

# Number of pure pixels per class
NumberPurePixels = np.zeros((numberOfClasses), np.uint16)

# Create LC samples map
Samples = np.zeros((rows,cols), np.uint16)

for i, lc_class in enumerate( classes ):
    # For some udersampled clasess apply a lenient threshold
    # Improved grassland = 3
    if lc_class == 1 :
        indices = np.where ( ( mode_LC == lc_class ) & \
                             ( mean_LC >= lc_class ) & \
                             ( mean_LC <= lc_class + 0.25 ) )
    elif lc_class == 3 :
        indices = np.where ( ( mode_LC == lc_class ) & \
                             ( mean_LC >= lc_class - 0.01 ) & \
                             ( mean_LC <= lc_class + 0.01 ) )
    elif lc_class == 4 :
        indices = np.where ( ( mode_LC == lc_class ) & \
                             ( mean_LC >= lc_class - 0.05 ) & \
                             ( mean_LC <= lc_class + 0.05 ) )
    elif lc_class == 22 :
        indices = np.where ( ( mode_LC == lc_class ) & \
                             ( mean_LC >= lc_class ) & \
                             ( mean_LC <= lc_class + 0.1 ) )
    elif lc_class == 23 :
        indices = np.where ( ( mode_LC == lc_class ) & \
                             ( mean_LC >= lc_class - 0.2 ) & \
                             ( mean_LC <= lc_class ) )
    else:
        # Get the total number of pure pixels per class
        indices = np.where( mean_LC == lc_class )

    Samples[ indices[0], indices[1] ] = lc_class
    NumberPurePixels[i] = indices[0].shape[0]

TotalNumberPurePixels = NumberPurePixels.sum().astype(float)

for i, lc_class in enumerate( classes ):
    print lc_class, proportion[i], NumberPurePixels[i] / TotalNumberPurePixels, NumberPurePixels[i]

print "Writing results to a file..."
format = "ENVI"
driver = gdal.GetDriverByName(format)

new_dataset = driver.Create('Samples.img', cols, rows, 1, GDT_UInt16)
new_dataset.GetRasterBand(1).WriteArray(Samples[:,:])
new_dataset = None

