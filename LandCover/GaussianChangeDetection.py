import numpy as np
import osgeo.gdal as gdal
import time

from multiprocessing import Process, Array

try:
    import sharedmem as shm
except ImportError:
    print 'Numpy/SharedMemory is not installed.'

def computeCartesian( PixelToProcess ):

    row, col = indices_mask[0][PixelToProcess], indices_mask[1][PixelToProcess]
    #print row, col

    lcp_profile = lcp[:,row,col]
    # Reshape into a numberOfYears x numberOfClasses array
    lcp_profile = lcp_profile.reshape( numberOfYears, numberOfClasses )
    # Get the cartesian product of all lcc probabilities
    product = cartesian( lcp_profile ).prod( axis = 1 )
    product_max = product.max()
    if product_max == 0.0:
        # There are probs eq 0 for some LC -- investigate
        return( -1 )

    # Sort relevant probabilities
    indices_subset = np.where( product > ( product_max * 0.3 ) )
    # if there are not enough elements
    decrement = 0.01
    while indices_subset[0].shape[0] < 10 :
        indices_subset = np.where( product > ( product.max() * ( 0.1 - decrement ) ) )
        decrement = decrement + 0.01

    indices_fullsorted = np.argsort( product[ indices_subset ] )[-10:]

    lcc_prob[row,col,:] = np.flipud( product[ indices_subset[0][ indices_fullsorted ] ] )
    lcc_traj[row,col,:] = merge_array(
            np.flipud( classesTrajectories[ indices_subset[0][ indices_fullsorted ] ] ) )

    return( 0 )

def merge_array( landCoverTrajectories ):
    trajectories = np.zeros( ( landCoverTrajectories.shape[0] ), np.uint64 )
    for i, row in enumerate( landCoverTrajectories ):
        value = ''
        for cell in row:
            value = value + str(cell)

        trajectories[i] = np.uint64( value )

    return trajectories

def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    """

    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([n, len(arrays)], dtype=dtype)

    m = n / arrays[0].size
    out[:,0] = np.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m,1:])
        for j in xrange(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out

numberOfClasses = 7
numberOfYears = 8

print 'Reading data...'
# Load per class, per year LC probilities
DataDir = '/home/dn907640/MELODIES/data/MODIS/processing/mosaics/Classification/Aggregated'
fname = DataDir + '/' + 'MELODIES_LCP_Agg.img'
lcp = gdal.Open( fname ).ReadAsArray()
numberOfBands, rows, cols = lcp.shape

# Get only the last 10 years of data
lc_years = numberOfBands / numberOfClasses
lcp = lcp[ ( ( lc_years - numberOfYears ) * numberOfClasses ) : ]

# Get masl
fname = DataDir + '/' + 'NumberOfAggLC_changes_masked.tif'
mask = gdal.Open( fname ).ReadAsArray()

# Default trajectories for all classes/years
classes = np.repeat( np.arange( 1, numberOfClasses + 1 ), numberOfYears ) \
                      .reshape( numberOfClasses, numberOfYears ).T
classesTrajectories = cartesian( classes )

# Output arrays
# LC change probabilities
lcc_prob = shm.zeros( (rows, cols, 10 ), dtype = np.float32 )
# LC change trajectories
lcc_traj = shm.zeros( (rows, cols, 10 ), dtype = np.uint64 )

# Processing only pixels where there was a LC change
print 'Processing only pixels where there was a LC change...'
indices_mask = np.where( mask > 0 )
print 'Total number of pixels to process:', indices_mask[0].shape[0]
# Aprox 347k pixels

Processes = []
NumProcesses = 8 # Number of cores available to do the processing

PixelToProcess = 0
# Run until all the threads are done, and there is no pixels to process
while Processes or PixelToProcess < indices_mask[0].shape[0]:
    # if we aren't using all the processors AND there is interpolations left to
    # compute, then spawn another thread
    if ( len( Processes ) < NumProcesses ) and PixelToProcess < indices_mask[0].shape[0]:

        p = Process( target = computeCartesian, args = [ PixelToProcess ])

        p.daemon = True
        p.name = str( PixelToProcess )
        p.start()
        Processes.append(p)

        PixelToProcess += 1

    # in case that we have the maximum number of threads check
    # if any of them are done.
    else:
        for process in Processes:
            if not process.is_alive():
                Processes.remove(process)
                if int(process.name) % 100 == 0:
                    print process.name, 'processed'

# Save output files
output_dir = DataDir + '/' + 'Changes'
drv = gdal.GetDriverByName ("GTiff")
dst_ds = drv.Create ( "%s/LC_change_prob.tif" % ( output_dir ), \
    cols, rows, 10, gdal.GDT_Float64, \
    options=["COMPRESS=LZW", "INTERLEAVE=BAND", "TILED=YES"] )

for i in range( numberOfYears ):
    dst_ds.GetRasterBand( i + 1 ).WriteArray ( lcc_prob[:,:,i] )

dst_ds = None


output_dir = DataDir + '/' + 'Changes'
drv = gdal.GetDriverByName ("GTiff")
dst_ds = drv.Create ( "%s/LC_change_trajectories.tif" % ( output_dir ), \
    cols, rows, 10, gdal.GDT_Float64, \
    options=["COMPRESS=LZW", "INTERLEAVE=BAND", "TILED=YES"] )

for i in range( numberOfYears ):
    dst_ds.GetRasterBand( i + 1 ).WriteArray ( lcc_traj[:,:,i] )

dst_ds = None
