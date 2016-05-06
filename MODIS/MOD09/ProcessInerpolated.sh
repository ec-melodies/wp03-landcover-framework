#!/bin/sh

year=$1

DATADIR=$HOME/MELODIES/data/MODIS/processing/mosaics/$year
SRCDIR=$HOME/MELODIES/src/MODIS/MOD09

cd $DATADIR/interpolated

for band in 3 4 5 6
do
	echo $SRCDIR/Interpolate.py $DATADIR/$year.f0.b$band.Wings.vrt \
                           $DATADIR/$year.NSamples.Wings.vrt \
                           $DATADIR/$year.GoF.Wings.vrt

	exit

	$SRCDIR/Interpolate.py $DATADIR/$year.f0.b$band.Wings.vrt \
                           $DATADIR/$year.NSamples.Wings.vrt \
                           $DATADIR/$year.GoF.Wings.vrt
done
