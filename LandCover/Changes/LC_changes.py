#!/bin/env python

import osgeo.gdal as gdal
import numpy as np

import sys

lcc_fname = sys.argv[1]
lcc = gdal.Open( lcc_fname ).ReadAsArray()

lcp_fname = sys.argv[2]
lcp = gdal.Open( lcp_fname ).ReadAsArray()

numberOfChanges_fname = sys.argv[3] 
numberOfChanges = gdal.Open( numberOfChanges_fname ).ReadAsArray()

# Analyse only pixels where numberOfChanges > 0
indices = np.where( numberOfChanges > 0 )

for index in range( indices[0].shape[0] ):

    from IPython import embed
    ipshell = embed()

    r, c = indices[0][index], indices[1][index]
    # Transform LC class into lcp array indices
    # there are 7 classes
    lcc_profile = lcc[:,r,c]
    lcp_indices = lcc_profile + 0
    for i, lcp_index in enumerate( lcp_indices ):
        lcp_indices[i] = ( lcp_index - 1 ) + ( i * 7 )
