#!/bin/env python

import numpy as np
import glob
import sys

from IPython import embed

from multiprocessing import Process, Array
from scipy.stats import pearsonr

try:
    import sharedmem as shm
except ImportError:
    print 'Numpy/SharedMemory is not installed.'

try:
    import osgeo.gdal as gdal
    from osgeo.gdalconst import *
    gdal.UseExceptions()
except ImportError:
    print 'GDAL is not installed.'
    exit(-1)

# AVHRR-LTDR projection information
#sys.path.append('/home/glopez/GCII/src/AVHRR-LTDR')
#from ProjectionInfo import *

def GetDimensions(File):
    dataset = gdal.Open(File, GA_ReadOnly)
    rows, cols, NumberOfBands = dataset.RasterYSize, dataset.RasterXSize, dataset.RasterCount
    dataset = None

    return rows, cols, NumberOfBands

DataDir = '/home/dn907640/MELODIES/data/MODIS'
year = sys.argv[1]
# LC time series is 2003 to 2014
# therefore LC can be identified from 2004 onwards
baseYear = 2004

band = sys.argv[2]

print "Getting data..."
# Get BRDF f0 time series
fname = '%s/processing/mosaics/%s/interpolated/%s.only.f0.b%s.interpolated.vrt' \
        % ( DataDir, year, year, band )
f0 = gdal.Open( fname ).ReadAsArray()

# Get prior -> BRDF f0 climatology
fname = '%s/mosaics/Prior/f0.b%s.vrt' % ( DataDir, band )
f0_prior = gdal.Open( fname ).ReadAsArray()

# Get mask based on LC, avoid processing on water
fname = '%s/processing/mosaics/Classification/Aggregated/YearOfAggLC_changes_masked.tif' \
        % ( DataDir )
mask = gdal.Open( fname ).ReadAsArray()
mask = mask[ int( year ) - baseYear ]

# Create output array
layers, rows, cols = f0.shape
PearsonR = np.zeros( ( rows, cols, 2 ), np.float32 )

print "Computing Pearson R for time series..."
indices = np.where( mask >= 1 )
NumberOfPixels = indices[0].shape[0]
print "Number of pixels to process:", NumberOfPixels

for i in range( NumberOfPixels ):
    pctPixelsProcessed =  ( i * 100 ) / NumberOfPixels
    if pctPixelsProcessed % 10 == 0 :
        print "Pixeles processed:", pctPixelsProcessed, "%"

    row, col = indices[0][i], indices[1][i]
    f0_profile = f0[:,row,col]
    f0_prior_profile = f0_prior[:,row,col]

    PearsonRcoef, p_value = pearsonr( f0_profile, f0_prior_profile )    
    PearsonR[row,col,0] = PearsonRcoef
    PearsonR[row,col,1] = p_value

drv = gdal.GetDriverByName ("GTiff")
OutputDir = '%s/processing/mosaics/PearsonR' % ( DataDir ) 

dst_ds = drv.Create ( "%s/PearsonR.%s.b%s.tif" % ( OutputDir, year, band ), \
    cols, rows, 2, gdal.GDT_Float32, \
    options=["COMPRESS=LZW", "INTERLEAVE=BAND", "TILED=YES"] )

dst_ds.GetRasterBand( 1 ).WriteArray ( PearsonR[:,:,0] )
dst_ds.GetRasterBand( 2 ).WriteArray ( PearsonR[:,:,1] )

dst_ds = None


