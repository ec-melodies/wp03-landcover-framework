#!/bin/bash

FUNC=CreateMosaic.sh
echo ""
echo ${FUNC}: Checking command line arguments

if [ $# -ne 1 ]; then
    echo ""
    echo Usage: $FUNC DATADIR
    echo To create a layerstack of a global monthly mosaic of the MCD64A1:
    echo $FUNC /media/data3/GCII/data/MCD64A1/2001
    echo ""
    exit 1
fi

SRCDIR=/data/GCII/RadiativeForcing/v1/MCD64A1

DATADIR=$1
cd $DATADIR

Year=`basename $DATADIR`

if [ $Year -eq 2000 ] || [ $Year -eq 2004 ] || [ $Year -eq 2008 ] || [ $Year -eq 2012 ]; then
        DaysOfMonth="001 032 061 092 122 153 183 214 245 275 306 336"
        echo "Processing leap year $Year"
        echo "Days of month: $DaysOfMonth"
else
        DaysOfMonth="001 032 060 091 121 152 182 213 244 274 305 335"
        echo "Processing regular year $Year"
        echo "Days of month: $DaysOfMonth"
fi

# Extract from the MCD64A1 SDS only the Burn Data layer
for file in $DATADIR/*.hdf
do
    echo gdal_translate -of VRT HDF4_EOS:EOS_GRID:"$file":MOD_Grid_Monthly_500m_DB_BA:"Burn Date" $DATADIR/`basename $file hdf`BurnDate.vrt
    gdal_translate -of VRT HDF4_EOS:EOS_GRID:"$file":MOD_Grid_Monthly_500m_DB_BA:"Burn Date" $DATADIR/`basename $file hdf`BurnDate.vrt
done

# Reproject
for DoY in $DaysOfMonth
do
        gdalwarp -t_srs '+proj=longlat +ellps=clrk66 +no_defs' -te -180.0 -90.0 180.0 90.0 -tr 0.05 0.05 *$Year$DoY*vrt MCD64A1.A$Year$DoY.tif
done

gdal_merge.py -o MCD64A1.A$Year.MonthlyMosaic.tif -separate MCD64A1.A$Year???.tif
rm MCD64A1.A$Year???.tif

# Create annual composite
echo $SRCDIR/CreateAnnualComposite.py MCD64A1.A$Year.MonthlyMosaic.tif
$SRCDIR/CreateAnnualComposite.py MCD64A1.A$Year.MonthlyMosaic.tif

