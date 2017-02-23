__author__ = 'Jane'

try:
    import numpy as np
except ImportError:
    print 'Numpy is not installed.'
    exit(-1)

try:
    import osgeo.gdal as gdal
    from osgeo.gdalconst import *
    gdal.UseExceptions()
except ImportError:
    print 'GDAL is not installed.'
    exit(-1)

def GetDimensions(File):
    dataset = gdal.Open(File, GA_ReadOnly)
    rows, cols, NumberOfBands = dataset.RasterYSize, dataset.RasterXSize, dataset.RasterCount
    dataset = None

    return rows, cols, NumberOfBands

def GetStrDoY(DoY):

    if len(str(int(DoY))) == 1:
        strDoY = '00' + str(int(DoY))
    elif len(str(int(DoY))) == 2:
        strDoY = '0' + str(int(DoY))
    else:
        strDoY = str(int(DoY))

    return strDoY