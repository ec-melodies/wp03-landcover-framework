#!/bin/bash

source $HOME/.bashrc

init_time=`date`

SRCDIR=$HOME/MELODIES/src/MODIS/MOD09

DATADIR=$1 # e.g. /home/dn907640/MELODIES/data/MODIS
tile=$2
year=$3

for DoY in `seq 1 8 365`
do
	strDoY=`echo $DoY | awk '{ if (length($1)==1) printf("00%d", $1); else if (length($1)==2) printf("0%d", $1); else printf("%d", $1)}'`
    BRDF_NoSnow=$DATADIR/processing/$tile/NoSnow/BRDF_Parameters.$year$strDoY.$tile.img
    BRDF_Snow=$DATADIR/processing/$tile/Snow/BRDF_Parameters.$year$strDoY.$tile.Snow.img

    echo $SRCDIR/BHR.py $BRDF_NoSnow $BRDF_Snow $DATADIR/processing/$tile/BHR
    $SRCDIR/BHR.py $BRDF_NoSnow $BRDF_Snow $DATADIR/processing/$tile/BHR > $tile.$year$strDoY.log

done

echo "$init_time - `date`"
