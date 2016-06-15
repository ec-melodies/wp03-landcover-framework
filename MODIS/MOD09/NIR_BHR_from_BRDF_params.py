#!/usr/bin/env python

import sys

import osgeo.gdal as gdal
from osgeo.gdalconst import *
import numpy

BRDF = sys.argv[1]
print BRDF

#Get raster size
dataset = gdal.Open( BRDF, GA_ReadOnly )
ymax, xmax = dataset.RasterYSize, dataset.RasterXSize

# NIR and sigma NIR
NumberOfBands = 1
NumberOfParameters = 3

BHR = numpy.zeros((ymax, xmax, NumberOfBands), numpy.float32 )

#Get BRDF parameters
f0 = dataset.GetRasterBand(1).ReadAsArray() * 0.001
f1 = dataset.GetRasterBand(2).ReadAsArray() * 0.001
f2 = dataset.GetRasterBand(3).ReadAsArray() * 0.001

#f0_sd = numpy.sqrt(dataset.GetRasterBand(13).ReadAsArray())
#f1_sd = numpy.sqrt(dataset.GetRasterBand(14).ReadAsArray())
#f2_sd = numpy.sqrt(dataset.GetRasterBand(15).ReadAsArray())

BHR[:,:,0] = f0 + (f1 * 0.189184) + (f2 * -1.377622)
BHR[:,:,0] = numpy.where( ((BHR[:,:,0] < 0.0) | (BHR[:,:,0] > 0.72)), 0.0, BHR[:,:,0])

#BHR[:,:,1] = f0_sd + (f1_sd * 0.189184) + (f2_sd * -1.377622)
#BHR[:,:,1] = numpy.where( ((BHR[:,:,1] < 0.0) | (BHR[:,:,1] > 0.72)), 0.0, BHR[:,:,1])

format = "ENVI"
driver = gdal.GetDriverByName(format)

#new_dataset = driver.Create( sys.argv[1] + '.NIR_BHR.tif', xmax, ymax, NumberOfBands, GDT_Float32, ['COMPRESS=PACKBITS'] )
new_dataset = driver.Create( sys.argv[1] + '.NIR_BHR.img', xmax, ymax, NumberOfBands, GDT_Float32)
new_dataset.GetRasterBand(1).WriteArray(BHR[:,:,0])
#new_dataset.GetRasterBand(2).WriteArray(BHR[:,:,1])

new_dataset = None

