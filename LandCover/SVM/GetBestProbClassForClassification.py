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

# Get projection info from master file
fname = '/home/dn907640/MELODIES/data/LandCover/LCM/LandCoverMap_2007_25m_raster/data/sinosoidal/lcm2007_UK_sin500m_mode.tif'
d = gdal.Open( fname )
Projection = d.GetProjection()
GeoTransform = d.GetGeoTransform()
d = None

# =======
# Samples
# =======
samples_fname = sys.argv[1]
dataset = gdal.Open( samples_fname )
bands = dataset.RasterCount
samples = dataset.GetRasterBand(2).ReadAsArray()

# Get each LC class
# Get land cover classes
classes = np.unique( samples )
# Exclude fill value
fillValue = 0
classes = classes[np.where( classes <> fillValue )]

# ======================
# Input LC probabilities
# ======================
LC_prob_file = sys.argv[2]
dataset = gdal.Open( LC_prob_file )
cols, rows = dataset.RasterXSize, dataset.RasterYSize

LC_prob = dataset.ReadAsArray()

indices = LC_prob.argmax( axis = 0 )
indices = np.where ( LC_prob.sum( axis = 0 ) > 0, indices + 1, indices )
LCmaxProb = np.zeros( (indices.shape[0], indices.shape[1]), np.int8 )

# Set the corresponding class
for i, lc_class in enumerate( classes ):
    LCmaxProb = np.where( indices == i + 1, lc_class, LCmaxProb )
    #indices[ indices == i + 1 ] = lc_class

format = "GTiff"
driver = gdal.GetDriverByName(format)

# Most probable class
new_dataset = driver.Create( 'LCC_maxprob.tif', cols, rows, 1, gdal.GDT_Byte )
new_dataset.GetRasterBand(1).WriteArray( LCmaxProb )

new_dataset.SetProjection( Projection )
new_dataset.SetGeoTransform( GeoTransform )

new_dataset = None

