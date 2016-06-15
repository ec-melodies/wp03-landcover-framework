#!/bin/bash

DATADIR=$1
# e.g. /home/dn907640/MELODIES/data/MODIS/processing/mosaics

Year=$2
#e.g. 2007

cd $DATADIR/$Year/interpolated

for band in 1 2 5 7
do
    echo gdal_vrtmerge.py -o $Year.f0.b$band.interpolated.vrt -separate 20?????.f0.b$band.interpolated.img
    gdal_vrtmerge.py -o $Year.f0.b$band.interpolated.vrt -separate 20?????.f0.b$band.interpolated.img

    echo gdal_vrtmerge.py -o $Year.only.f0.b$band.interpolated.vrt -separate $Year???.f0.b$band.interpolated.img
    gdal_vrtmerge.py -o $Year.only.f0.b$band.interpolated.vrt -separate $Year???.f0.b$band.interpolated.img
done

