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

DataDir = '/home/dn907640/MELODIES/data/MODIS'
year = sys.argv[1]

print "Getting data..."
# Get correlations

fname = '%s/processing/mosaics/PearsonR/PearsonR.%s.b1.tif' \
        % ( DataDir, year )
f0_b1_corr = gdal.Open( fname ).ReadAsArray()
f0_b1_corr = f0_b1_corr[0]

fname = '%s/processing/mosaics/PearsonR/PearsonR.%s.b2.tif' \
        % ( DataDir, year )
f0_b2_corr = gdal.Open( fname ).ReadAsArray()
f0_b2_corr = f0_b2_corr[0]

fname = '%s/processing/mosaics/PearsonR/PearsonR.%s.b7.tif' \
        % ( DataDir, year )
f0_b7_corr = gdal.Open( fname ).ReadAsArray()
f0_b7_corr = f0_b7_corr[0]


mask = np.zeros_like( f0_b1_corr )

threshold = 0.5
indices = np.where( ( ( f0_b1_corr < threshold ) & ( f0_b1_corr <> 0 ) ) |
                    ( ( f0_b2_corr < threshold ) & ( f0_b2_corr <> 0 ) ) |
                    ( ( f0_b7_corr < threshold ) & ( f0_b7_corr <> 0 ) ) ) 

mask[ indices ] = 1

# Get projection info from master file
fname = '/home/dn907640/MELODIES/data/LandCover/LCM/LandCoverMap_2007_25m_raster/data/sinosoidal/lcm2007_UK_sin500m_mode.tif'
d = gdal.Open( fname )
Projection = d.GetProjection()
GeoTransform = d.GetGeoTransform()
d = None

drv = gdal.GetDriverByName ("GTiff")
OutputDir = '%s/processing/mosaics/PearsonR' % ( DataDir ) 

rows, cols = mask.shape

dst_ds = drv.Create ( "%s/Candidates.%s.tif" % ( OutputDir, year ), \
    cols, rows, 1, gdal.GDT_Byte, \
    options=["COMPRESS=LZW", "INTERLEAVE=BAND", "TILED=YES"] )

dst_ds.GetRasterBand( 1 ).WriteArray ( mask )

dst_ds.SetProjection( Projection )
dst_ds.SetGeoTransform( GeoTransform )

dst_ds = None


