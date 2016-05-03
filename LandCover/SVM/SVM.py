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
except ImportError:
  print "Scikit-learn is not installed"
  exit(-1)

import sys
import numpy as np

from IPython import embed

# ==============
# Input features
# ==============
NIR_fname = sys.argv[1]
dataset = gdal.Open( NIR_fname )
cols, rows, bands = dataset.RasterXSize, dataset.RasterYSize, dataset.RasterCount

NIR = dataset.ReadAsArray()

VIS_fname = sys.argv[2]
dataset = gdal.Open( VIS_fname )
cols, rows, bands = dataset.RasterXSize, dataset.RasterYSize, dataset.RasterCount

VIS = dataset.ReadAsArray()

# =======
# Samples
# =======
samples_fname = sys.argv[3]
dataset = gdal.Open( samples_fname )
cols, rows, bands = dataset.RasterXSize, dataset.RasterYSize, dataset.RasterCount

samples = dataset.GetRasterBand(1).ReadAsArray()

# Get each LC class
# Get land cover classes
classes = np.unique( samples )
# Exclude fill value
fillValue = 0
classes = classes[np.where( classes <> fillValue )]

# Array for training data
X = None
# Array for classes
y = None

for lc_class in classes:
    print "Getting samples for class", lc_class
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
        else:
            #X = np.vstack ( ( X , profile ) )
            X = np.vstack ( ( X , 
                 np.hstack ( ( NIR_profile , VIS_profile ) ) ) )
            y = np.append( y , lc_class )

# Create the SVM classifier
print "Trainning the classifier..."
clf = svm.SVC( probability = True )
clf.fit(X, y)

# Apply the classifier to get the class probabilities
classification = np.zeros ( ( rows, cols ), np.int8 )
probability = np.zeros ( ( rows, cols, classes.shape[0] ), np.float32 )
for j in range(0,cols):
    if j % 100 == 0:
        print "Processing columns", j
    for i in range(0,rows):
        profile = np.hstack( (NIR[:,i,j], VIS[:,i,j] ) )
        # if there are enough observations, apply the classifier
        if profile.nonzero()[0].shape[0] >= 30:
            classification[i,j] = clf.predict ( profile )[0]
            probability[i,j,:] = clf.predict_proba ( profile )[0]

format = "GTiff"
driver = gdal.GetDriverByName(format)

# Most probable class
new_dataset = driver.Create( 'LCC.tif', cols, rows, 1, gdal.GDT_Byte )
new_dataset.GetRasterBand(1).WriteArray(classification)
new_dataset = None

# Probability
new_dataset = driver.Create( 'LCP.tif', cols, rows, classes.shape[0], gdal.GDT_Float32 )
for band in range ( classes.shape[0] ):
    new_dataset.GetRasterBand(band+1).WriteArray(probability[:,:,band])

new_dataset = None

# Scores
#scores = clf.score( X , y)

#ipshell = embed()

#clf.decision_function ( profile )
