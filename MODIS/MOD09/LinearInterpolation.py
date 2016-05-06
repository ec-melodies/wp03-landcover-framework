
__author__ = "Gerardo López Saldaña"
__version__ = "0.1 (12.05.2013)"
__email__ = "GerardoLopez@isa.utl.pt"

import numpy
import glob
import sys

from IPython import embed

from multiprocessing import Process, Array
from scipy.interpolate import interp1d

try:
    import sharedmem as shm
except ImportError:
    print 'Numpy/SharedMemory is not installed.'

try:
    import osgeo.gdal as gdal
    from osgeo.gdalconst import *
    gdal.UseExceptions()
except ImportError:
    print 'GDAL is not installed.'
    exit(-1)

# AVHRR-LTDR projection information
#sys.path.append('/home/glopez/GCII/src/AVHRR-LTDR')
#from ProjectionInfo import *

def GetDimensions(File):
    dataset = gdal.Open(File, GA_ReadOnly)
    rows, cols, NumberOfBands = dataset.RasterYSize, dataset.RasterXSize, dataset.RasterCount
    dataset = None

    return rows, cols, NumberOfBands

def Interpolate(X, Y):
    # Interpolate where there is no data
    indices = numpy.where(Y<>0.0)
    x_with_data = X[indices[0]]
    y = Y[indices[0]]

    # find the first and last values on X
    index_first_element = numpy.where(X == x_with_data[0])
    index_last_element = numpy.where(X == x_with_data[-1])
    new_x = X[index_first_element[0][0]:index_last_element[0][0]]

    f = interp1d(x_with_data, y)
    interpolated_data = f(new_x)

    return new_x, interpolated_data

def ComputeInterpolation(LineToProcess, NumberOfCols):
    i = LineToProcess

    for j in range(0,NumberOfCols):
        NIR_profile = NIR[i,j,:]
        #if NIR_profile.nonzero()[0].shape[0] < (BandCount - (BandCount / 4)):
        if NIR_profile.nonzero()[0].shape[0] < 20:
            # If there are not enough observations continue
            InterpolatedNIR[i,j,:] = NIR_profile
            continue

        # if there are no data to interpolate
        if NIR_profile.nonzero()[0].shape[0] < 10:
            InterpolatedNIR[i,j,:] = NIR[i,j,:]
            continue

        X, InterpolatedNIR_profile = Interpolate(numpy.arange(BandCount), NIR_profile)
        InterpolatedNIR[i,j,X] = InterpolatedNIR_profile
        # If there are zeros in the interpolated time series
        # will fill it with the original values
        indices = numpy.where( InterpolatedNIR[i,j,:] == 0 )
        InterpolatedNIR[i,j,indices] = NIR[i,j,indices]


# ------------
# Get NIR data
# ------------
print 'Loading data...'
NIR_file = sys.argv[1]

try:
   print NIR_file
   NIR_dataset = gdal.Open( NIR_file, GA_ReadOnly )
   rows, cols, BandCount = GetDimensions(NIR_file)
   # Get band names and delete first band since is the name if the layerstack
   BandNames = NIR_dataset.GetFileList()
   BandNames.remove(BandNames[0])
except:
   print "Error:", sys.exc_info()[0]
   exit(-1)

# Create empty array
NIR = numpy.zeros((rows,cols,BandCount), numpy.float32)
InterpolatedNIR = shm.zeros((rows,cols,BandCount), dtype=numpy.float32)
# Populate array
for band in range(BandCount):
    NIR[:,:,band] = NIR_dataset.GetRasterBand(band+1).ReadAsArray()

NIR_dataset = None


Processes = []
NumProcesses = 12 # Number of cores available to do the processing

LineToProcess = 0
# Run until all the threads are done, and there is no pixels to process
while Processes or LineToProcess < rows:
    # if we aren't using all the processors AND there is interpolations left to
    # compute, then spawn another thread
    if (len(Processes) < NumProcesses) and LineToProcess < rows:

        p = Process(target=ComputeInterpolation, args=[LineToProcess, cols])

        p.daemon = True
        p.name = str(LineToProcess)
        p.start()
        Processes.append(p)

        LineToProcess += 1

    # in case that we have the maximum number of threads check
    # if any of them are done.
    else:
        for process in Processes:
            if not process.is_alive():
                Processes.remove(process)
                if int(process.name) % 100 == 0:
                    print process.name, 'processed'


#ipshell = embed()
print "Writing results to a file..."
format = "ENVI"
driver = gdal.GetDriverByName(format)

for i in range(BandCount):
    NewBandName = BandNames[i].split('/')[-1][0:-3] + 'interpolated.img'
    new_dataset = driver.Create(NewBandName, cols, rows, 1, GDT_Float32)
    new_dataset.GetRasterBand(1).WriteArray(InterpolatedNIR[:,:,i])

    #ProjectionInfo = GetProjectionInfo()
    #new_dataset.SetProjection(ProjectionInfo.Projection)
    #new_dataset.SetGeoTransform(ProjectionInfo.GeoTransform)

    new_dataset = None

