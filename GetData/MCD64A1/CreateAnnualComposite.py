#!/bin/env python

__author__ = "Gerardo Lopez-Saldana (UREAD)"
__copyright__ = "(c) 2014"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "G Lopez-Saldana"
__email__ = "G.LopezSaldana@reading.ac.uk"
__status__ = "Development"

import sys

try:
  import numpy
except ImportError:
  print 'Numpy is not installed'
  exit(-1)

try:
  import osgeo.gdal as gdal
  from osgeo.gdalconst import *
  gdal.UseExceptions()
except ImportError:
  print 'GDAL is not installed.'
  exit(-1)

# AVHRR-LTDR projection information
sys.path.append('/data/GCII/RadiativeForcing/v1')
from ProjectionInfo import *

def GetDimensions(File):
    dataset = gdal.Open(File, GA_ReadOnly)
    rows, cols, NumberOfBands = dataset.RasterYSize, dataset.RasterXSize, dataset.RasterCount
    dataset = None

    return rows, cols, NumberOfBands

InputFile = sys.argv[1]

print InputFile
rows, cols, NumberOfBands = GetDimensions(InputFile)
dataset = gdal.Open( InputFile, GA_ReadOnly )

# Output array
MonthlyBA = numpy.zeros((rows, cols, NumberOfBands), numpy.int16)

for i in range(NumberOfBands):
    data = dataset.GetRasterBand(i+1).ReadAsArray()
    data = numpy.where((data >= 1) & (data < 366), data, 0)
    MonthlyBA[:,:,i] = data

MonthlyBA = numpy.ma.masked_equal(MonthlyBA, 0)

indices = numpy.mgrid[0:MonthlyBA.shape[0], 0:MonthlyBA.shape[1]]
indices_min = MonthlyBA.argmin(axis=2)
AnnualBA = MonthlyBA[indices[0], indices[1], indices_min]

format = "GTiff"
driver = gdal.GetDriverByName(format)
filename = InputFile.split('.')[0] + '.' + InputFile.split('.')[1] + '.AnnualComposite.tif'
new_dataset = driver.Create(filename, cols, rows, 1, GDT_Int16, ['COMPRESS=PACKBITS'] )
new_dataset.GetRasterBand(1).WriteArray(AnnualBA[:,:])

ProjectionInfo = GetProjectionInfo()
new_dataset.SetProjection(ProjectionInfo.Projection)
new_dataset.SetGeoTransform(ProjectionInfo.GeoTransform)

new_dataset = None
