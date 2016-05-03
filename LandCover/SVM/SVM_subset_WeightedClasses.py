#!/usr/bin/env python

try:
  import osgeo.gdal as gdal
  from osgeo.gdalconst import *
  gdal.UseExceptions()
except ImportError:
  print "GDAL is not installed."
  exit(-1)

try:
  from sklearn import svm
  from sklearn.externals import joblib
except ImportError:
  print "Scikit-learn is not installed"
  exit(-1)

try:
    import sharedmem as shm
except ImportError:
    print 'Numpy/SharedMemory is not installed.'

from multiprocessing import Process, Array

import sys
import pickle
import numpy as np

from IPython import embed

def DoClassification( LineToProcess, iCol, eCol ):

    i = LineToProcess
    for j in range( iCol, eCol + 1 ):
        profile = np.hstack( (NIR[:,i,j], VIS[:,i,j] ) )
        if profile.nonzero()[0].shape[0] >= 30:
            classification[i,j] = clf.predict ( profile )[0]
            probability[i,j,:] = clf.predict_proba ( profile )[0]

iRow = 0
iCol = 0
eRow = 2458
eCol = 1988

rows = (eRow - iRow)
cols = (eCol - iCol)

# ==============
# Input features
# ==============
NIR_fname = sys.argv[1]
dataset = gdal.Open( NIR_fname )
bands = dataset.RasterCount
NIR = dataset.ReadAsArray()

VIS_fname = sys.argv[2]
dataset = gdal.Open( VIS_fname )
bands = dataset.RasterCount
VIS = dataset.ReadAsArray()

# =======
# Samples
# =======
samples_fname = sys.argv[3]
dataset = gdal.Open( samples_fname )
bands = dataset.RasterCount
samples = dataset.GetRasterBand(2).ReadAsArray()
#samples = dataset.ReadAsArray()

# Sample weights
samples_w_fname = sys.argv[4]
# second colums is the original class area proportion
samples_w = np.loadtxt( samples_w_fname )[:,1]

# Get each LC class
# Get land cover classes
classes = np.unique( samples )
# Exclude fill value
fillValue = 0
classes = classes[np.where( classes <> fillValue )]

# ============================
# If there is a trainned model
# ============================
if len ( sys.argv ) == 6:
    SVM_clf = sys.argv[5] # pkl file, e.g. MELODIES_SVM_clf.pkl
    clf = joblib.load( SVM_clf )
else:

    # Array for training data
    X = None
    # Array for classes
    y = None

    for class_index, lc_class in enumerate( classes ):
        print "Getting samples for class", lc_class, "weight:", samples_w[ class_index ]
        indices = np.where ( samples == lc_class )
        for i in range ( len ( indices[0] ) ):
            row, col = indices[0][i], indices[1][i]
            # f0 temporal profile
            NIR_profile = NIR[:,row,col]
            VIS_profile = VIS[:,row,col]

            if X == None:
                #X = np.column_stack ( profile )
                X = np.hstack ( ( NIR_profile , VIS_profile ) )
                y = np.array( [ lc_class ] )
                class_weight = np.array( [ samples_w[ class_index ] ] )
            else:
                #X = np.vstack ( ( X , profile ) )
                X = np.vstack ( ( X , 
                     np.hstack ( ( NIR_profile , VIS_profile ) ) ) )
                y = np.append( y , lc_class )
                class_weight = np.append( class_weight, samples_w[ class_index ] )

    # Create the SVM classifier
    ipshell = embed()
    print "Trainning the classifier..."
    kernel='rbf'
    #class_weight = 'auto'
    probability = True
    cache_size=200
    clf = svm.SVC( kernel = kernel,
                   probability = probability, cache_size = cache_size )
    clf.fit(X, y, class_weight)

    # Save the trainned model
    # To load: clf = joblib.load('MELODIES_SVM_clf.pkl')
    print "Saving the model..."
    joblib.dump(clf, 'MELODIES_SVM_clf.pkl') 

# Shared memory output arrays
classification = shm.zeros ( ( NIR.shape[1], NIR.shape[2] ), dtype = np.int8 )
probability = shm.zeros ( ( NIR.shape[1], NIR.shape[2], classes.shape[0] ), dtype = np.float32 )

Processes = []
NumProcesses = 12 # Number of cores available to do the processing

LineToProcess = iRow
# Run until all the threads are done, and there is no pixels to process
while Processes or LineToProcess < eRow:

    # if we aren't using all the processors AND there is interpolations left to
    # compute, then spawn another thread
    if (len(Processes) < NumProcesses) and LineToProcess < eRow:

        p = Process(target = DoClassification, args=[LineToProcess, iCol, eCol])

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
                if int(process.name) % 10 == 0:
                    print process.name, 'processed'


format = "GTiff"
driver = gdal.GetDriverByName(format)

# Most probable class
new_dataset = driver.Create( 'LCC_subset.tif', NIR.shape[2], NIR.shape[1], 1, gdal.GDT_Byte )
new_dataset.GetRasterBand(1).WriteArray(classification)
new_dataset = None

# Probability
new_dataset = driver.Create( 'LCP_subset.tif', NIR.shape[2], NIR.shape[1], classes.shape[0], gdal.GDT_Float32 )
for band in range ( classes.shape[0] ):
    new_dataset.GetRasterBand(band+1).WriteArray(probability[:,:,band])

new_dataset = None

# Scores
#scores = clf.score( X , y)

#ipshell = embed()

#clf.decision_function ( profile )
