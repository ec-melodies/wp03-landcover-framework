#!/bin/bash

SRCDIR=$HOME/MELODIES/src/GetData

tiles=`cat $HOME/GlobAlbedo/src/Sites.txt | cut -d" " -f 4`
product=LAI

for tile in $tiles
do
	for year in `seq 2002 2004`
	do
		DATADIR=$HOME/MELODIES/data/GLASS/$tile/$year
		mkdir -p $DATADIR
		cd $DATADIR

		echo $SRCDIR/get_data_from_GLCF.csh $product $year $tile 1
		$SRCDIR/get_data_from_GLCF.csh $product $year $tile 1
		#$SRCDIR/get_data_from_LPDAAC.csh $product $year $tile 49
	done
done
