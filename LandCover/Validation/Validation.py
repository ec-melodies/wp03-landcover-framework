#!/usr/bin/env python

try:
    import osgeo.gdal as gdal
    from osgeo.gdalconst import *
    gdal.UseExceptions()
except ImportError:
    print 'GDAL is not installed.'
    exit(-1)

try:
    import numpy as np
except ImportError:
    print 'NumPy is not installed.'
    exit(-1)

import sys
from sklearn.metrics import confusion_matrix

try:
    import matplotlib as mpl
    mpl.use('Agg')
    from pylab import *

except ImportError:
    print 'MatPlotLib/PyLab is not installed.'
    exit(-1)

from IPython import embed

def plot_confusion_matrix(cm, title='MELODIES LC 2007 - Confusion matrix', cmap=plt.cm.Blues):

    ClassNames = [ 'Broadleaved Woodland', 'Coniferous Woodland',
                  'Arable and Horticulture', 'Improved Grassland',
                  'Rough Grassland', 'Calcareous Grassland',
                  'Fen, Marsh and Swamp', 'Heather',
                  'Heather Grassland', 'Bog',
                  'Montane Habitats', 'Inland Rock',
                  'Saltwater', 'Freshwater',
                  'Supra-littoral Rock', 'Supra-littoral sediment',
                  'Littoral Rock', 'Littoral Sediment',
                  'Saltmarsh', 'Urban', 'Suburban' ]

    plt.imshow(cm, interpolation = 'nearest', cmap = cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len( ClassNames ))
    plt.xticks(tick_marks, ClassNames, rotation = 90 )
    #[t.set_color('red') for t in ax.xaxis.get_ticklabels()]


    plt.yticks(tick_marks, ClassNames )
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

def GetDimensions(File):
    dataset = gdal.Open(File, GA_ReadOnly)
    rows, cols, NumberOfBands = dataset.RasterYSize, dataset.RasterXSize, dataset.RasterCount
    dataset = None

    return rows, cols, NumberOfBands

LC_fname = sys.argv[1]

rows, cols, NumberOfBands = GetDimensions( LC_fname )
dataset = gdal.Open( LC_fname , GA_ReadOnly )
LC = dataset.ReadAsArray()
# Get pixel size (should be a squared pixel and size in meters)
geoTransform = dataset.GetGeoTransform()
pixelSize = geoTransform[1]
del ( dataset )

validation_fname = sys.argv[2]
dataset = gdal.Open( validation_fname , GA_ReadOnly )
validation = dataset.GetRasterBand(2).ReadAsArray()
del ( dataset )

# Get land cover classes
classes = np.unique( validation )
# Exclude fill value
fillValue = 0
classes = classes[np.where( classes <> fillValue )]

y_true = np.array([])
y_pred = np.array([])

for i, lc_class in enumerate( classes ):

    print "Validating class", lc_class
    #ipshell = embed()

    indices = np.where ( validation == lc_class )

    PercentOfSamplesToKeep = 0.2
    r_indices = np.random.randint( 0, high = indices[0].shape[0],
                      size = int( indices[0].shape[0] * PercentOfSamplesToKeep ) )

    indices = ( indices[0][r_indices], indices[1][r_indices] )

    y_true = np.append( y_true, validation[ indices ] )
    y_pred = np.append( y_pred, LC[ indices ] )


matplotlib.rc('xtick', labelsize = 5) 
matplotlib.rc('ytick', labelsize = 5)

# Create confusion matrix
np.set_printoptions(precision=2)
cm = confusion_matrix(y_true, y_pred)

cm = np.ma.masked_equal( cm, 0. )
cmap = plt.cm.Blues
cmap._init()
cmap.set_bad( '0.9', 1. )

plt.figure()
plot_confusion_matrix( cm, cmap = cmap )
savefig( 'CM.png', dpi = 250, bbox_inches='tight' )

# Normalize the confusion matrix by row (i.e by the number of samples
# in each class)
cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

cm_normalized = np.ma.masked_equal( cm_normalized, 0. )
cmap = plt.cm.Blues
cmap._init()
cmap.set_bad( '0.9', 1. )

plt.figure()
plot_confusion_matrix(cm_normalized, 
  title = 'MELODIES LC 2007 - Normalized confusion matrix', cmap = cmap )

savefig( 'CM_normalized.png', dpi = 250, bbox_inches='tight' )

