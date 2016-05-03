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


landCoverFile = sys.argv[1]
maskFile = sys.argv[2]
# /home/dn907640/MELODIES/data/LandCover/LCM/LandCoverMap_2007_25m_raster/data/sinosoidal/lcm2007_UK_sin500m_mode.tif

rows, cols, NumberOfBands = GetDimensions( landCoverFile )

dataset = gdal.Open( landCoverFile , GA_ReadOnly )
# Get pixel size (should be a squared pixel and size in meters)
#geoTransform = dataset.GetGeoTransform()
#pixelSize = geoTransform[1]
pixelSize = 463.312716527916677
# How many hectars per pixel - 500m pixel size
hectarsPerPixel = ( pixelSize  ** 2 ) / ( 100 ** 2 )

landCover = dataset.GetRasterBand(1).ReadAsArray()

mask = gdal.Open( maskFile ).ReadAsArray()
mask = np.where( mask <> 0, 1, 0 )

landCover = landCover * mask

# Get land cover classes
classes = np.unique( landCover )
# Exclude fill value
fillValue = 0
# Exclude water from stats
Saltwater = 15
Freshwater = 16

indices = np.where( ( classes <> fillValue  ) &
                    ( classes <> Saltwater ) &
                    ( classes <> Freshwater ) )

classes = classes[ indices ]

# Total number of pixels
totalArea = np.where( ( landCover <> fillValue ) &
                      ( landCover <> Saltwater ) &
                      ( landCover <> Freshwater ) )[0].shape[0] * hectarsPerPixel
print totalArea

numberOfClasses = classes.shape[0]
classArea = np.zeros((numberOfClasses, 3), np.float32)

# Store results in a text file
f = open( 'MELODIES_LC_stats.txt', 'w' )

for i, lc_class in enumerate( classes ):
    # Land cover class
    classArea[i,0] = lc_class
    # Area
    classArea[i,1] = np.where( landCover == lc_class )[0].shape[0] * hectarsPerPixel
    # Percent
    classArea[i,2] = classArea[i,1] / totalArea

    #f.write( str(classArea[i,0]) + ' ' + str(classArea[i,1]) + ' ' 
    #         + str(classArea[i,2]) + ' ' + str( np.where( landCover == lc_class )[0].shape[0] ) + '\n' )

    f.write( "%d %.4f %d\n" % ( classArea[i,0], classArea[i,2], classArea[i,1]  ) )

    #print classArea[i,0], classArea[i,1], classArea[i,2], np.where( landCover == lc_class )[0].shape[0]
    print classArea[i,0], classArea[i,2], classArea[i,1]

f.close()

