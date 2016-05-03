#!/usr/bin/env python

import sys
import calendar
import os

import gdal
import numpy as np
from scipy.stats import mode

from IPython import embed

GDAL2NUMPY = {  gdal.GDT_Byte      :   np.uint8,
                gdal.GDT_UInt16    :   np.uint16,
                gdal.GDT_Int16     :   np.int16,
                gdal.GDT_UInt32    :   np.uint32,
                gdal.GDT_Int32     :   np.int32,
                gdal.GDT_Float32   :   np.float32,
                gdal.GDT_Float64   :   np.float64,
                gdal.GDT_CInt16    :   np.complex64,
                gdal.GDT_CInt32    :   np.complex64,
                gdal.GDT_CFloat32  :   np.complex64,
                gdal.GDT_CFloat64  :   np.complex128
              }

def aggregate_function ( LC_data, LC_class, fillValue = 0 ):

    # Only compute the LC fraction for land pixels
    land = ( LC_data != fillValue).sum()

    # Number of pixels corresponding to the LC class
    lc = np.where ( LC_data == LC_class )[0].shape[0]

    if land.sum() > 0 and lc > 0:
        # Compute LC fraction
        LC_fraction = ( 1. * lc ) / ( 1. * land)
        return LC_fraction

    elif land.sum() > 0 and lc == 0:
        # Some unclassified on land pixels...
        return 0
    else:
        return -1

def aggregate_data ( LC_hr_fname, LC_cr_fname , 
                     input_lc_fillValue, output_lc_fillValue, 
                     aggregate_function, LC_classes ):

    LC_cr_d = gdal.Open( LC_cr_fname )
    gt_cr = LC_cr_d.GetGeoTransform()

    # Size of the output raster
    res_x = LC_cr_d.RasterXSize
    res_y = LC_cr_d.RasterYSize

    output_grid = np.zeros( ( res_y, res_x, LC_classes.shape[0] ) )

    # Open LC dataset
    LC_hr_d = gdal.Open( LC_hr_fname )
    gt_hr = LC_hr_d.GetGeoTransform()

    # Sixe of the original rasters
    nx = LC_hr_d.RasterXSize
    ny = LC_hr_d.RasterYSize

    #ipshell = embed()

    # Size of the block to read data from original rasters
    #block_size = [ np.ceil ( nx / float(nx_blocks) ), \
    #               np.ceil ( ny / float(ny_blocks) ) ]
    block_size = [ float(LC_hr_d.RasterXSize) / res_x , 
                   float(LC_hr_d.RasterYSize) / res_y ]

    nx_valid = block_size[0]
    ny_valid = block_size[1]

    # Data types
    LC_dt = GDAL2NUMPY[ LC_hr_d.GetRasterBand(1).DataType ]

    for X in xrange( res_x ):
        print X
        if X == res_x - 1:
            nx_valid = nx - X * block_size[0]
            buf_size = int ( nx_valid * ny_valid )

        # find X offset
        this_X = int ( X * block_size[0] )

        # reset buffer size for start of Y loop
        ny_valid = block_size[1]
        buf_size = int ( nx_valid * ny_valid )

        # loop through Y lines
        for Y in xrange( res_y ):
            # change the block size of the final piece
            if Y == res_y - 1:
                ny_valid = ny - Y * block_size[1]
                buf_size = int ( nx_valid * ny_valid )

            # find Y offset
            this_Y = int ( Y * block_size[1] )

            # def ReadRaster(self, xoff, yoff, xsize, ysize,
            #       buf_xsize = None, buf_ysize = None, buf_type = None,
            #       band_list = None ):

            # The xoff, yoff, xsize, ysize parameter define the rectangle on the raster file
            # to read.  The buf_xsize, buf_ysize values are the size of the resulting
            # buffer.  So you might say "0,0,512,512,100,100" to read a 512x512 block
            # at the top left of the image into a 100x100 buffer (downsampling the image). 

            buf = LC_hr_d.ReadRaster(this_X, this_Y, int(nx_valid), int(ny_valid), \
                        buf_xsize = int(nx_valid), buf_ysize = int(ny_valid), \
                        band_list = [1] )

            LC_data = np.frombuffer ( buf, dtype = LC_dt )

            if np.nonzero( LC_data )[0].sum() > 0:
                for i, lc_class in enumerate( LC_classes ):
                    LC_fraction = aggregate_function ( LC_data, 
                                                       lc_class, 
                                                       input_lc_fillValue )
                    output_grid[ Y, X, i ] = LC_fraction 
                    #ipshell = embed()
            else:
                output_grid[ Y, X, : ] = output_lc_fillValue

    return output_grid

# High resolution
# This file must be the actual file with 
# the high resolution LC map original projection
LC_hr_fname = sys.argv[1]

# Coarse resolution
# This file can be a VRT dataset to know
# what would be the output dimensions
# and the geographic projection needed
LC_cr_fname = sys.argv[2]

# Fill values
input_lc_fillValue = int ( sys.argv[3] )
output_lc_fillValue = int ( sys.argv[4] )

print "Finding number of classes to resample..."
tmp_lc = gdal.Open( LC_hr_fname ).ReadAsArray()
LC_classes = np.unique ( tmp_lc )

LC_classes = LC_classes[ np.where( LC_classes <> input_lc_fillValue ) ]
del tmp_lc
#LC_classes = np.array( [2, 3] )

# Open coarse resolution LC dataset
# to extract the output file dimensions
LC_cr_d = gdal.Open( LC_cr_fname )
gt = LC_cr_d.GetGeoTransform()
proj = LC_cr_d.GetProjection()

res_x = LC_cr_d.RasterXSize
res_y = LC_cr_d.RasterYSize

output_grid = np.zeros(( res_y, res_x, LC_classes.shape[0] ))

output_grid[:,:,:] = aggregate_data ( LC_hr_fname, LC_cr_fname,
                                      input_lc_fillValue, output_lc_fillValue,
                                      aggregate_function, LC_classes )

output_dir = "./"
param = "LC_fraction"
product = "LCM"
year = 2007

drv = gdal.GetDriverByName ("GTiff")
dst_ds = drv.Create ( "%s/%s.%s.%04d.tif" % ( output_dir, param, product, year ), \
    res_x, res_y, LC_classes.shape[0], gdal.GDT_Float32, \
    options=["COMPRESS=LZW", "INTERLEAVE=BAND", "TILED=YES"] )

dst_ds.SetGeoTransform( gt )
dst_ds.SetProjection ( proj )

# Write output dataset
for i in range( LC_classes.shape[0] ):
    dst_ds.GetRasterBand( i + 1 ).WriteArray ( \
        np.where ( output_grid[:,:,i] == -1, -1, (output_grid[:,:,i])).astype(np.float32) )

    dst_ds.GetRasterBand( i + 1 ).SetNoDataValue ( -1 )

dst_ds = None

