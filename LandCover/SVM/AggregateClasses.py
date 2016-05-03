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

InitYear = 2003
EndYear = 2014
NumberOfClasses = 7
# 1 - Forest
# 2 - Crops
# 3 - Grass
# 4 - Wetlands
# 5 - Urban / Suburban
# 6 - Bare soil
# 7 - Water

# Get land cover probabilities
for i, year in enumerate( range( InitYear, EndYear + 1 ) ):

    print 'Procesing:', year
    lc_probs = gdal.Open( 'LCP.%d.tif' % ( year) ).ReadAsArray()
    ( layers, rows, cols ) = lc_probs.shape

    lc_agg_probs = np.zeros( ( 7, rows, cols ), np.float32 )

    # There are no probs for classes (1-based index):
    # 6 - Neutral grassland
    # 9 - Fen, marsh and swamp
    lc_probs = np.insert( lc_probs, [5,7], np.zeros( ( rows, cols ), np.float32 ), axis = 0 )

    # Group Forest = Broadleave woodland +Coniferus woodland
    lc_agg_probs[0] = lc_probs[0] + lc_probs[1]
    # Crops = Arable and Horticulture
    lc_agg_probs[1] = lc_probs[2]
    # Group grasses
    lc_agg_probs[2] = lc_probs[3] + lc_probs[4] + lc_probs[5] + lc_probs[6] + lc_probs[7]
    # Group wetlands
    lc_agg_probs[3] = lc_probs[8] + lc_probs[9] + lc_probs[10] + lc_probs[11] + lc_probs[20]
    # Group urban
    lc_agg_probs[4] = lc_probs[21] + lc_probs[22]
    # Group bare soil
    lc_agg_probs[5] = lc_probs[12] + lc_probs[13] + lc_probs[16] + \
                      lc_probs[17] + lc_probs[18] +  lc_probs[19]
    # Group water
    lc_agg_probs[6] = lc_probs[14] + lc_probs[15]

    # Save aggregated lc classes for this year
    fname = 'LCP_Agg.%d.tif' % ( year)

    drv = gdal.GetDriverByName ("GTiff")
    dst_ds = drv.Create ( fname, cols, rows, 7, gdal.GDT_Float32, \
        options=["COMPRESS=LZW", "INTERLEAVE=BAND", "TILED=YES"] )

    # Write output dataset
    for j in range( 7 ):
        dst_ds.GetRasterBand( j + 1 ).WriteArray ( lc_agg_probs[j] )

    dst_ds = None


