#!/bin/bash

DATADIR=$1
# e.g. /home/dn907640/MELODIES/data/MODIS/processing/mosaics

Year=$2
#e.g. 2007

PreviousYear=`echo $Year - 1 | bc`
FollowingYear=`echo $Year + 1 | bc`

# Create mosaics for each spectral band
for band in `seq 1 7`
do
    gdal_vrtmerge.py -o $DATADIR/$Year/$Year.f0.b$band.Wings.vrt -separate \
                     $DATADIR/$PreviousYear/${PreviousYear}3??.f0.b$band.vrt \
                     $DATADIR/$Year/$Year???.f0.b$band.vrt \
                     $DATADIR/$FollowingYear/${FollowingYear}0[0-5]?.f0.b$band.vrt
done

# Create mosaics for GoF
gdal_vrtmerge.py -o $DATADIR/$Year/$Year.GoF.Wings.vrt -separate \
                 $DATADIR/$PreviousYear/${PreviousYear}3??.GoF.vrt \
                 $DATADIR/$Year/$Year???.GoF.vrt \
                 $DATADIR/$FollowingYear/${FollowingYear}0[0-5]?.GoF.vrt

# Creae mosaics for NSamples
gdal_vrtmerge.py -o $DATADIR/$Year/$Year.NSamples.Wings.vrt -separate \
                 $DATADIR/$PreviousYear/${PreviousYear}3??.NSamples.vrt \
                 $DATADIR/$Year/$Year???.NSamples.vrt \
                 $DATADIR/$FollowingYear/${FollowingYear}0[0-5]?.NSamples.vrt
