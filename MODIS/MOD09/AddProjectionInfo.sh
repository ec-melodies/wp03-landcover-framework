#!/bin/bash

tile=$1
year=$2

DATADIR="/home/dn907640/MELODIES/data/MODIS/processing/$tile/NoSnow"
SRCDIR=$HOME/MELODIES/src/MODIS/MOD09

cd $DATADIR

for file in $DATADIR/BRDF_Parameters.$year???.$tile.hdr
do
	grep -q Sinusoidal $file
	if [ $? -eq 0 ] ; then
		#file has projection info
		echo "$file has projection information"
	else
		echo 
		echo $file
		cat $file $SRCDIR/MapInfo/MapInfo.$tile > tmp.txt
		mv -f tmp.txt $file
	fi
done


