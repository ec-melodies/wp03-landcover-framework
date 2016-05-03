#!/bin/bash

SRCDIR=$HOME/MELODIES/src/GetData

tile=$1
product=$2 # MCD43A4 for instance

DATADIR=$HOME/MELODIES/data/MODIS/$tile/$product
#mkdir -p $DATADIR
#cd $DATADIR

#for year in `seq 2000 2000`
for year in `seq 2001 2006`
do
	$SRCDIR/get_data_from_LPDAAC.csh $product $year $tile 1
	#$SRCDIR/get_data_from_LPDAAC.csh $product $year $tile 49
done
