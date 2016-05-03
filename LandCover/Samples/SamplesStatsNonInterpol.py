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

try:
    import matplotlib as mpl
    mpl.use('Agg')
    from pylab import *

    import datetime as DT
    from matplotlib.dates import date2num
    from matplotlib.dates import MonthLocator, DateFormatter

except ImportError:
    print 'MatPlotLib/PyLab is not installed.'
    exit(-1)

import sys
from IPython import embed

def GetDimensions(File):
    dataset = gdal.Open(File, GA_ReadOnly)
    rows, cols, NumberOfBands = dataset.RasterYSize, dataset.RasterXSize, dataset.RasterCount
    dataset = None

    return rows, cols, NumberOfBands

samples_fname = sys.argv[1]
band = sys.argv[2]
band_name = sys.argv[3]

rows, cols, NumberOfBands = GetDimensions( samples_fname )
dataset = gdal.Open( samples_fname , GA_ReadOnly )

LC_samples = dataset.ReadAsArray()

print "Getting LC classes..."
# Get land cover classes
classes = np.unique( LC_samples )
# Exclude fill value
fillValue = 0
classes = classes[np.where( classes <> fillValue )]

print "Getting surface reflectance data..."
# Surface reflectance data
datadir = "/home/dn907640/MELODIES/data/MODIS/processing/mosaics/2007"
b = gdal.Open( datadir + '/' + '2007.f0.b' + band + '.vrt').ReadAsArray()
#b = gdal.Open( datadir + '/' + '2007.f0.b' + band + '.interpolated.img').ReadAsArray()

# File to store sample stats
f_mean = open( 'LC_samples_mean.txt', 'a+' )
f_std = open( 'LC_samples_std.txt', 'a+' )

# x-axis is a single year
year = 2007
DoY = np.arange( 1, 365, 8 )
GregDoY = np.zeros( ( DoY.shape[0] ) , np.float32 )
for i, day in enumerate( DoY ):
    date = DT.datetime.strptime( "%d%03d" % ( year, day ) , "%Y%j" )
    GregDoY[i] = date2num( date )

ClassName = ['',
             'Broadleaved Woodland', 'Coniferous Woodland',
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

# Plot temporal profiles per LC class samples
for lc_class in classes:
#for lc_class in [3, 4]:
    print "Plotting data for class:", ClassName[ lc_class ]
    indices = np.where( LC_samples == lc_class )

    # Create new plot
    fig, ax = plt.subplots( figsize = ( 11,6 ) )

    # Compute mean
    for i in range ( indices[0].shape[0] ):
        profile = b[ :, indices[0][i], indices[1][i] ]
        plot_date( GregDoY, profile , '-', lw = 0.15 )

        if i == 0 :
            sum_lc = np.zeros( (profile.shape[0] ) )
        else:
            sum_lc = sum_lc + profile

    mean_lc = sum_lc / ( i - 1 )

    # Compute SD
    for j in range ( indices[0].shape[0] ):
        profile = b[ :, indices[0][j], indices[1][j] ]
        if j == 0 :
            squared_diff_sum = np.zeros( (profile.shape[0] ) )
        else:
            squared_diff_sum = squared_diff_sum + np.power( ( profile - mean_lc ), 2 )

    std_lc = np.sqrt( ( 1 / ( i - 1. ) ) * squared_diff_sum )

    plot_date( GregDoY, mean_lc, '-', color='black', lw = 1.5 )

    fill = fill_between( GregDoY,
                  mean_lc - std_lc,
                  mean_lc + std_lc,
                  alpha=0.3, edgecolor='black',
                  facecolor='black')
    fill.set_zorder( i + 2 )

    # Save class stats
    f_mean.write( str(lc_class) + " " + band + " " + \
                   " ".join( map( str, mean_lc ) ) + "\n" )
    f_std.write( str(lc_class) + " " + band + " " + \
                   " ".join( map( str, std_lc ) ) + "\n" )
   
    ax.grid(True)
    ax.format_xdata = DateFormatter('%m')
    fig.autofmt_xdate()

    ax.set_xlabel("Month")
    ax.set_ylabel(band_name + ' Surface Reflectance' )

    ax.set_title( ClassName[ lc_class ] )
 
    #savefig ( "Class_" + str(lc_class) + ".band" + band + ".pdf", dpi = 100, bbox_inches='tight' )
    savefig ( "Class_" + str(lc_class) + ".band" + band + ".png", dpi = 200, bbox_inches='tight' )
    close()

f_mean.close()
f_std.close()

