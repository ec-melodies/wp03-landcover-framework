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

# Get land cover classification
lc = gdal.Open( 'MELODIES_LC.img' ).ReadAsArray()

for i, year in enumerate( range( InitYear, EndYear + 1 ) ):

    annual_lc = lc[i]

    print 'Procesing:', year
    lc_probs = gdal.Open( 'LCP.%d.tif' % ( year) ).ReadAsArray()
    ( layers, rows, cols ) = lc_probs.shape

    # Output matrices
    lc_agg_probs = np.zeros( ( 7, rows, cols ), np.float32 )
    annual_agg_lc = np.zeros( ( rows, cols ), np.byte )

    # There are no probs for classes (1-based index):
    # 6 - Neutral grassland
    # 9 - Fen, marsh and swamp
    lc_probs = np.insert( lc_probs, [5,7], np.zeros( ( rows, cols ), np.float32 ), axis = 0 )

    # 1 - Group Forest = Broadleave woodland +Coniferus woodland
    lc_agg_probs[0] = lc_probs[0] + lc_probs[1]
    class_IDs = np.array( [1,2] )
    ix = np.in1d( annual_lc.ravel(), class_IDs ).reshape( annual_lc.shape)
    annual_agg_lc[ np.where( ix ) ] = 1

    # 2 - Crops = Arable and Horticulture
    lc_agg_probs[1] = lc_probs[2]
    class_IDs = np.array( [3] )
    ix = np.in1d( annual_lc.ravel(), class_IDs ).reshape( annual_lc.shape)
    annual_agg_lc[ np.where( ix ) ] = 2

    # 3 - Group grasses
    lc_agg_probs[2] = lc_probs[3] + lc_probs[4] + lc_probs[5] + \
                      lc_probs[6] + lc_probs[7] + lc_probs[9] +  lc_probs[10]
    class_IDs = np.array( [4,5,6,7,8,10,11] )
    ix = np.in1d( annual_lc.ravel(), class_IDs ).reshape( annual_lc.shape)
    annual_agg_lc[ np.where( ix ) ] = 3

    # 4 - Group wetlands
    lc_agg_probs[3] = lc_probs[8] + lc_probs[11] + lc_probs[20]
    class_IDs = np.array( [9,12,21] )
    ix = np.in1d( annual_lc.ravel(), class_IDs ).reshape( annual_lc.shape)
    annual_agg_lc[ np.where( ix ) ] = 4

    # 5 - Group urban
    lc_agg_probs[4] = lc_probs[21] + lc_probs[22]
    class_IDs = np.array( [22,23] )
    ix = np.in1d( annual_lc.ravel(), class_IDs ).reshape( annual_lc.shape)
    annual_agg_lc[ np.where( ix ) ] = 5

    # 6 - Group bare soil
    lc_agg_probs[5] = lc_probs[12] + lc_probs[13] + lc_probs[16] + \
                      lc_probs[17] + lc_probs[18] +  lc_probs[19]
    class_IDs = np.array( [13,14,17,18,19,20] )
    ix = np.in1d( annual_lc.ravel(), class_IDs ).reshape( annual_lc.shape)
    annual_agg_lc[ np.where( ix ) ] = 6

    # 7 - Group water
    lc_agg_probs[6] = lc_probs[14] + lc_probs[15]
    class_IDs = np.array( [15,16] )
    ix = np.in1d( annual_lc.ravel(), class_IDs ).reshape( annual_lc.shape)
    annual_agg_lc[ np.where( ix ) ] = 7

    '''
    print "Checking probabilities..."
    # Check that the lc agg prob match the classification
    # other wise, rearange the probs
    indices_non_zeros = np.nonzero( annual_agg_lc )

    for k in range( indices_non_zeros[0].shape[0] ):
        r,c = indices_non_zeros[0][k], indices_non_zeros[1][k]

        indices_sorted = np.argsort( lc_agg_probs[:,r,c] )

        if annual_agg_lc[r,c] <> indices_sorted[-1] + 1:
            lc_agg_probs[ annual_agg_lc[r,c]- 1, r, c ], lc_agg_probs[ indices_sorted[-1], r, c ] = \
                lc_agg_probs[ indices_sorted[-1], r, c ], lc_agg_probs[ annual_agg_lc[r,c] - 1, r, c ]
    '''

    # Get projection info from master file
    fname = '/home/dn907640/MELODIES/data/LandCover/LCM/LandCoverMap_2007_25m_raster/data/sinosoidal/lcm2007_UK_sin500m_mode.tif'
    d = gdal.Open( fname )
    Projection = d.GetProjection()
    GeoTransform = d.GetGeoTransform()
    d = None

    # Save aggregated lc classes probs for this year
    fname = 'LCP_Agg.%d.tif' % ( year)

    drv = gdal.GetDriverByName ("GTiff")
    dst_ds = drv.Create ( fname, cols, rows, 7, gdal.GDT_Float32, \
        options=["COMPRESS=LZW", "INTERLEAVE=BAND", "TILED=YES"] )

    # Write output dataset
    for j in range( 7 ):
        dst_ds.GetRasterBand( j + 1 ).WriteArray ( lc_agg_probs[j] )

    dst_ds.SetProjection( Projection )
    dst_ds.SetGeoTransform( GeoTransform )

    dst_ds = None

    # Save aggregated lc classes probs for this year
    fname = 'LCC_Agg.%d.tif' % ( year)
    dst_ds = drv.Create ( fname, cols, rows, 1, gdal.GDT_Byte, \
        options=["COMPRESS=LZW", "INTERLEAVE=BAND", "TILED=YES"] )

    dst_ds.GetRasterBand( 1 ).WriteArray ( annual_agg_lc )

    dst_ds.SetProjection( Projection )
    dst_ds.SetGeoTransform( GeoTransform )

    dst_ds = None
