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

ClassNames = [ 'Broadleaved Woodland', 'Coniferous Woodland',
              'Arable and Horticulture', 'Improved Grassland',
              'Rough Grassland', 'Neutral Grassland',
              'Calcareous Grassland', 'Acid Grassland',
              'Fen, Marsh and Swamp', 'Heather',
              'Heather Grassland', 'Bog',
              'Montane Habitats', 'Inland Rock',
              'Saltwater', 'Freshwater',
              'Supra-littoral Rock', 'Supra-littoral sediment',
              'Littoral Rock', 'Littoral Sediment',
              'Saltmarsh', 'Urban', 'Suburban' ]


LCP_fname = sys.argv[1]

row = 1873
col = 1655

d = gdal.Open( LCP_fname )
LCP = d.ReadAsArray( col, row, 1, 1)

from IPython import embed

del ( d )

classes = np.arange(1, 24)

ax = plt.subplot()
plt.bar( classes, LCP )

# add some text for labels, title and axes ticks
ax.set_ylabel('Probability')
ax.set_xticklabels( ( classes.astype( '|S2' )  ) )

savefig( 'vector.png', dpi = 250, bbox_inches='tight' )

