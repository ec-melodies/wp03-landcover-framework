#!/bin/bash

source $HOME/.bashrc

FUNC=MOD09_ComputeAllKernels.sh
echo ""
echo ${FUNC}: Checking command line arguments

if [ $# -lt 3 ]; then
    echo ""
    echo Usage: $FUNC TILE PRODUCT YEAR
    echo To compute all set of kernels for MOD09GA tile h17v03 during 2007
    echo $FUNC h17v03 MOD09GA 2007 [Optional DoY]
    echo ""
    exit 1
fi

init_time=`date`
echo $init_time

tile=$1
product=$2
year=$3

DoY=$4
if [ ${#DoY} -eq 0 ]; then
	DoY='???'
elif [ ${#DoY} -eq 1 ]; then
	DoY="${DoY}??"
fi

WORKDIR=`pwd`

# Scientific Data Records to extract
SDS_Type="HDF4_EOS:EOS_GRID"
SDR=("MODIS_Grid_1km_2D:state_1km_1" \
     "MODIS_Grid_1km_2D:SensorZenith_1" "MODIS_Grid_1km_2D:SensorAzimuth_1" \
     "MODIS_Grid_1km_2D:SolarZenith_1" "MODIS_Grid_1km_2D:SolarAzimuth_1" )
NumberOfSDRs=`echo ${#SDR[@]} - 1 | bc -l`

SRCDIR=$HOME/MELODIES/src/MODIS/MOD09
DATADIR=$HOME/MELODIES/data/MODIS/$tile/$product
OUTDIR=$HOME/MELODIES/data/MODIS/$tile/$product/Kernels

# MOD09 file name layout
#MOD09GA.A2007011.h17v04.005.2008134180033.hdf

for file in `ls $DATADIR/$product.A$year$DoY.$tile.*.*.hdf`
do
	TMPDIR=$OUTDIR/$$
	mkdir -p $TMPDIR
	cd $TMPDIR

	echo $file
    NumberOfSDR=`echo ${#SDR[@]} - 1 | bc -l`

    # Get DoY to process
    strDoY=`basename $file | cut -d. -f2 | cut -c6-8`

    for i in `seq 0 $NumberOfSDRs`
	do
        echo ""
        echo ${SDR[$i]}
		OutputFilename=$TMPDIR/`echo ${SDR[$i]} | cut -d: -f2`.vrt
        PixelSize=`echo ${SDR[$i]} | cut -d: -f1 | cut -d_ -f3`

        if [ $PixelSize == "500m" ]; then
            echo "gdal_translate -of VRT $SDS_Type:$file:${SDR[$i]} $OutputFilename"
            gdal_translate -of VRT $SDS_Type:$file:${SDR[$i]} $OutputFilename
        else
            echo "gdal_translate -of VRT -outsize 200% 200% $SDS_Type:$file:${SDR[$i]} $OutputFilename"
            gdal_translate -of VRT -outsize 200% 200% $SDS_Type:$file:${SDR[$i]} $OutputFilename
        fi
	done

	# Create anglular data layerstack
	gdal_vrtmerge.py -o angles.vrt -separate *Zenith*vrt *Azimuth*vrt

	# Mask surface reflectance using QA flags and compute kernels
	python $SRCDIR/ComputeKernels.py

    # Rename output files
    mv $TMPDIR/SDS_layerstack_kernels_masked.tif $OUTDIR/$product.$year$strDoY.$tile.kernels.tif

    cd $WORKDIR
    # Remove tmp files
    rm -rf $TMPDIR

done

echo "$init_time - `date`"
