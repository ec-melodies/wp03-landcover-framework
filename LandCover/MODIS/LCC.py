#!/usr/bin/env python

try:
  import osgeo.gdal as gdal
  from osgeo.gdalconst import *
  gdal.UseExceptions()
except ImportError:
  print 'GDAL is not installed.'
  exit(-1)

import sys
import numpy

dataset = gdal.Open( sys.argv[1] )

cols, rows, bands = dataset.RasterXSize, dataset.RasterYSize, dataset.RasterCount

LC = numpy.zeros((rows,cols,bands), numpy.int8)
for band in range(bands):
    LC[:,:,band] = dataset.GetRasterBand(band + 1).ReadAsArray()

LCC = numpy.zeros((rows,cols), numpy.int8)

for band in range(bands - 1):
    LCC = numpy.where( LC[:,:,band+1] - LC[:,:,band] <> 0, LCC + 1 , LCC )

format = "GTiff"
driver = gdal.GetDriverByName(format)

new_dataset = driver.Create( 'LCC.tif', cols, rows, 1, gdal.GDT_Byte )

from IPython import embed
ipshell = embed()

new_dataset.GetRasterBand(1).WriteArray(LCC[:,:])
new_dataset = None
