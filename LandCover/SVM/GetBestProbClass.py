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

from IPython import embed

# ======================
# Input LC probabilities
# ======================
year = sys.argv[1]
LC_prob_file = 'LCP.' + year + '.tif'
dataset = gdal.Open( LC_prob_file )
cols, rows = dataset.RasterXSize, dataset.RasterYSize

LC_prob = dataset.ReadAsArray()

indices = LC_prob.argmax( axis = 0 )
indices = np.where ( LC_prob.sum( axis = 0 ) > 0, indices + 1, indices )

format = "GTiff"
driver = gdal.GetDriverByName(format)

# Most probable class
new_dataset = driver.Create( 'LCC_MaxProb.' + year + '.tif', \
    cols, rows, 1, gdal.GDT_Byte, \
    options=["COMPRESS=LZW", "INTERLEAVE=BAND", "TILED=YES"] )

new_dataset.GetRasterBand(1).WriteArray( indices )
new_dataset = None
