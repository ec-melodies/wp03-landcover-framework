#!/bin/bash

SRCDIR=$HOME/MELODIES/src/GetData
DATADIR=$HOME/MELODIES/data

tile=$1
product=$2 # MCD43A4 for instance

#for year in `seq 2000 2000`
for year in `seq 2003 2013`
do
	$SRCDIR/get_data_from_LPDAAC.csh $product $year $tile 1
	#$SRCDIR/get_data_from_LPDAAC.csh $product $year $tile 49
done
