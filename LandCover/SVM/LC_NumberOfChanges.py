#!/usr/bin/env python

try:
  import osgeo.gdal as gdal
  from osgeo.gdalconst import *
  gdal.UseExceptions()
except ImportError:
  print "GDAL is not installed."
  exit(-1)

import sys
import numpy as np

fname = sys.argv[1]
mask_fname = sys.argv[2]

# data must be an array of layers * rows * cols
data = gdal.Open( fname ).ReadAsArray()
( layers, rows, cols ) = data.shape

# Mask non-data or 'Salt water'
# e.g. NumberOfLC_changes_masked.img
mask = gdal.Open( mask_fname ).ReadAsArray()
indices_zero = np.where( mask == -1 )

# Number of changes from one class to another
NumberOfChanges = np.where( np.diff( data, axis = 0 ) == 0, 0, 1 ).sum( axis = 0 )
NumberOfChanges[ indices_zero ] = -1

# Get year for change
YearOfChanges = np.where( np.diff( data, axis = 0 ) == 0, 0, 1 )
YearOfChanges[ :, indices_zero[0], indices_zero[1] ] = -1

# Save number of changes in yearly aggregated LC
fname = 'NumberOfAggLC_changes_masked.tif'
drv = gdal.GetDriverByName ("GTiff")
dst_ds = drv.Create ( fname, cols, rows, 1, gdal.GDT_Int16, \
    options=["COMPRESS=LZW", "INTERLEAVE=BAND", "TILED=YES"] )

dst_ds.GetRasterBand( 1 ).WriteArray ( NumberOfChanges )

dst_ds = None

# Save year of change
fname = 'YearOfAggLC_changes_masked.tif'
drv = gdal.GetDriverByName ("GTiff")
numberOfBands = YearOfChanges.shape[0]
dst_ds = drv.Create ( fname, cols, rows, numberOfBands, gdal.GDT_Int16, \
    options=["COMPRESS=LZW", "INTERLEAVE=BAND", "TILED=YES"] )

for i in range( numberOfBands ):
    dst_ds.GetRasterBand( i + 1 ).WriteArray ( YearOfChanges[i] )

dst_ds = None
