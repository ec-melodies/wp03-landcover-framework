#!/usr/bin/env python

import os
import sys

try:
  import sharedmem as shm
except ImportError:
  print 'Numpy/SharedMemory is not installed.'

from multiprocessing import Process

# AVHRR-LTDR projection information
#sys.path.append('/home/glopez/GCII/src/AVHRR-LTDR')
#from ProjectionInfo import *
#ProjectionInfo = GetProjectionInfo()

import osgeo.gdal as gdal
from osgeo.gdalconst import *
import numpy
import glob

from IPython import embed

def GetDimensions(File):
    dataset = gdal.Open(File, GA_ReadOnly)
    rows, cols, NumberOfBands = dataset.RasterYSize, dataset.RasterXSize, dataset.RasterCount
    dataset = None

    return rows, cols, NumberOfBands

def ComputeBHR(LineToProcess, columns, NumberOfBands, BRDFNoSnow, BRDFSnow):

    # Ge the proportion of NoSnow and Snow samples
    SumNSamples = BRDFNoSnow.NSamples + BRDFSnow.NSamples
    NoSnowProportion = numpy.divide( BRDFNoSnow.NSamples, SumNSamples )
    SnowProportion = numpy.divide( BRDFSnow.NSamples, SumNSamples )

    # Compute bihemispherical reflectance
    # BHR coefficients
    g = numpy.zeros((NumberOfParameters,1))
    g[0,0] = 1.0
    g[1,0] = 0.189184
    g[2,0] = -1.377622

    #ipshell = embed()

    i = LineToProcess
    for band in range( NumberOfBands ):
        for j in range( columns ):
            if BRDFNoSnow.f0[i,j,band] <> 0.0 or BRDFSnow.f0[i,j,band] <> 0.0 :
                TotalNSamples = BRDFNoSnow.NSamples[i,j] + BRDFSnow.NSamples[i,j]
                if TotalNSamples > 0. and \
                   BRDFNoSnow.f0[i,j,band] <> 0.0 and \
                   BRDFSnow.f0[i,j,band] <> 0.0:
                    # Calculate proportion of Snow and NoSnow samples
                    NoSnowProportion =  BRDFNoSnow.NSamples[i,j] / TotalNSamples
                    SnowProportion = BRDFSnow.NSamples[i,j] / TotalNSamples
                elif BRDFNoSnow.f0[i,j,band] <> 0.0 and BRDFNoSnow.NSamples[i,j] > 0.:
                    # There are no samples, use the NoSnow prior
                    NoSnowProportion = 1.
                    SnowProportion = 0.
                elif BRDFSnow.f0[i,j,band] <> 0.0 and BRDFSnow.NSamples[i,j] > 0.:
                    # There are no samples, use the Snow prior
                    SnowProportion = 1.
                    NoSnowProportion = 0.
                else:
                    # There are no samples at all - use NoSnow prior
                    NoSnowProportion = 1.
                    SnowProportion = 0.

                f0 = ( BRDFNoSnow.f0[i,j,band] * NoSnowProportion ) + \
                     ( BRDFSnow.f0[i,j,band] * SnowProportion )

                f1 = ( BRDFNoSnow.f1[i,j,band] * NoSnowProportion ) + \
                     ( BRDFSnow.f1[i,j,band] * SnowProportion )

                f2 = ( BRDFNoSnow.f2[i,j,band] * NoSnowProportion ) + \
                     ( BRDFSnow.f2[i,j,band] * SnowProportion )

                BHR[i,j,band] = f0 + (f1 * 0.189184) + (f2 * -1.377622)
                BHR[i,j,band] =  numpy.where( ((BHR[i,j,band] < 0.0) | (BHR[i,j,band] > 1.0)), 
                                             0.0, BHR[i,j,band])
                # BHR coefficients
                g = numpy.zeros((NumberOfParameters,1))
                g[0,0] = 1.0
                g[1,0] = 0.189184
                g[2,0] = -1.377622

                C = numpy.zeros((NumberOfParameters,NumberOfParameters))
                diag_indices = numpy.diag_indices( C.shape[0] )

                f0_var = ( BRDFNoSnow.f0_var[i,j,band] * NoSnowProportion ) + \
                     ( BRDFSnow.f0_var[i,j,band] * SnowProportion )

                f1_var = ( BRDFNoSnow.f1_var[i,j,band] * NoSnowProportion ) + \
                     ( BRDFSnow.f1_var[i,j,band] * SnowProportion )

                f2_var = ( BRDFNoSnow.f2_var[i,j,band] * NoSnowProportion ) + \
                     ( BRDFSnow.f2_var[i,j,band] * SnowProportion )

                C[ diag_indices[0], diag_indices[1] ] = [ f0_var, f1_var, f2_var ]
                C = numpy.matrix( C )

                try:
                    # Estimate the uncertainty as std
                    # f^T C^-1 f
                    BHR[i,j,band + NumberOfBands] = numpy.sqrt( (g.T * C.I * g).I )
                    UncertScalingFactor = 0.2
                    BHR[i,j,band + NumberOfBands] = numpy.where( ((BHR[i,j,band + NumberOfBands] < 0.0) | \
                             (BHR[i,j,band + NumberOfBands] > 1.0)), BHR[i,j,band] * UncertScalingFactor, \
                             BHR[i,j,band + NumberOfBands])
                except numpy.linalg.LinAlgError:
                    #ipshell = embed()
                    UncertScalingFactor = 0.2
                    BHR[i,j,band + NumberOfBands] =  BHR[i,j,band] * UncertScalingFactor

                # Snow proportion
                BHR[i,j,-1] = SnowProportion

def GetBRDF(BRDF_file, NumberOfBands = 7, NumberOfParameters = 3):

    # Check that file exists
    File = glob.glob( BRDF_file )
    if len(File) == 1:
        #Get raster size
        dataset = gdal.Open( BRDF_file, GA_ReadOnly )
        rows, cols, Bands = GetDimensions( BRDF_file )
    else:
        # File does not exist, create onlt empty array with nominal tile size
        rows = 2400
        cols = 2400

    #Get BRDF parameters
    f0 = shm.zeros((rows,cols, NumberOfBands), dtype = numpy.float32)
    f1 = shm.zeros((rows,cols, NumberOfBands), dtype = numpy.float32)
    f2 = shm.zeros((rows,cols, NumberOfBands), dtype = numpy.float32)

    f0_var = shm.zeros((rows,cols, NumberOfBands), dtype = numpy.float32)
    f1_var = shm.zeros((rows,cols, NumberOfBands), dtype = numpy.float32)
    f2_var = shm.zeros((rows,cols, NumberOfBands), dtype = numpy.float32)

    # Number of weighted samples used for BRDF inversion
    NSamples = shm.zeros((rows,cols), dtype = numpy.float32)

    if len(File) == 1:
        # Fill BRDF parameters array
        for band in range( NumberOfBands ):
            f0[:,:,band] = dataset.GetRasterBand((band * NumberOfParameters) + 1).ReadAsArray()
            f1[:,:,band] = dataset.GetRasterBand((band * NumberOfParameters) + 2).ReadAsArray()
            f2[:,:,band] = dataset.GetRasterBand((band * NumberOfParameters) + 3).ReadAsArray()

            f0_var[:,:,band] = dataset.GetRasterBand((band * NumberOfParameters) + \
                           (NumberOfParameters * NumberOfBands) + 1).ReadAsArray()
            f1_var[:,:,band] = dataset.GetRasterBand((band * NumberOfParameters) + \
                           (NumberOfParameters * NumberOfBands) + 2).ReadAsArray()
            f2_var[:,:,band] = dataset.GetRasterBand((band * NumberOfParameters) + \
                           (NumberOfParameters * NumberOfBands) + 3).ReadAsArray()

        NSamples = dataset.GetRasterBand( ((NumberOfParameters * NumberOfBands) * 2) + 2).ReadAsArray()

    return ReturnGetBRDF(f0, f1, f2, f0_var, f1_var, f2_var, NSamples)

class ReturnGetBRDF(object):
    def __init__(self, f0, f1, f2, f0_var, f1_var, f2_var, NSamples):
        self.f0 = f0
        self.f1 = f1
        self.f2 = f2
        self.f0_var = f0_var
        self.f1_var = f1_var
        self.f2_var = f2_var
        self.NSamples = NSamples


# ============== #

BRDFNoSnowFile = sys.argv[1]
print BRDFNoSnowFile
BRDFNoSnow = GetBRDF( BRDFNoSnowFile )

BRDFSnowFile = sys.argv[2]
print BRDFSnowFile
BRDFSnow = GetBRDF( BRDFSnowFile )

OutputDir = sys.argv[3]

# First 7 MODIS bands
rows = 2400
cols = 2400
NumberOfBands = 7
NumberOfParameters = 3
# Output array - reflectance bands, corresponding uncer, and Snow proportion
BHR = shm.zeros( (rows,cols, (NumberOfBands * 2) + 1 ), dtype = numpy.float32)

Processes = []
NumProcesses = 12 # Number of cores available to do the processing

LineToProcess = 0
ComputeBHR(LineToProcess, cols, NumberOfBands, BRDFNoSnow, BRDFSnow)

while Processes or LineToProcess < rows:
    # if we aren't using all the processors AND there are lines left to
    # compute, then spawn another thread
    if (len(Processes) < NumProcesses) and LineToProcess < rows:
        p = Process( target = ComputeBHR, args=[LineToProcess, cols, NumberOfBands, BRDFNoSnow, BRDFSnow] )

        p.daemon = True
        p.name = str(LineToProcess)
        print 'Starting process', str(LineToProcess)
        p.start()
        Processes.append(p)

        LineToProcess += 1
    # in case that we have the maximum number of threads check
    # if any of them are done.
    else:
        for process in Processes:
            if not process.is_alive():
                Processes.remove(process)
                print 'Line', process.name, 'processed'

format = "ENVI"
driver = gdal.GetDriverByName(format)

#new_dataset = driver.Create( sys.argv[1] + '.NIR_BHR.tif', xmax, ymax, NumberOfBands, GDT_Float32, ['COMPRESS=PACKBITS'] )
filename = os.path.basename(BRDFNoSnowFile)[0:-3]
new_dataset = driver.Create( OutputDir + '/' + filename + 'BHR.img', cols, rows, (NumberOfBands * 2) + 1, GDT_Float32)
for band in range( NumberOfBands ):
    new_dataset.GetRasterBand(band + 1).WriteArray(BHR[:,:,band])
    new_dataset.GetRasterBand(band + NumberOfBands + 1).WriteArray(BHR[:,:,band + NumberOfBands])

new_dataset.GetRasterBand((NumberOfBands * 2) + 1).WriteArray(BHR[:,:,-1])

#new_dataset.SetProjection(ProjectionInfo.Projection)
#new_dataset.SetGeoTransform(ProjectionInfo.GeoTransform)

new_dataset = None
