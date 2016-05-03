#!/bin/bash

tile=$1
DATADIR=$HOME/MELODIES/data/MODIS/$tile/MCD12Q1

mkdir -p $DATADIR/VRTs

cd $DATADIR/VRTs

for file in $DATADIR/*.hdf
do
    echo "gdal_translate -of VRT HDF4_EOS:EOS_GRID:"$file":MOD12Q1:Land_Cover_Type_1 `basename .hdf`.Land_Cover_Type_1.vrt"
    gdal_translate -of VRT HDF4_EOS:EOS_GRID:"$file":MOD12Q1:Land_Cover_Type_1 `basename $file .hdf`.Land_Cover_Type_1.vrt
done

echo "gdal_vrtmerge.py -o $tile.Land_Cover_Type_1.vrt MCD12Q1.A???????.$tile.*.Land_Cover_Type_1.vrt"
gdal_vrtmerge.py -o $tile.Land_Cover_Type_1.vrt MCD12Q1.A???????.$tile.*.Land_Cover_Type_1.vrt
