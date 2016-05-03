#!/bin/bash

SRCDIR=$HOME/src/MCD64A1/Aggregate

# /group_workspaces/cems2/nceo_generic/users/jlgomezdans/gls
DATADIR=$1
Year=$2
Resolution=$3

if [ $Year -eq 2000 ] || [ $Year -eq 2004 ] || [ $Year -eq 2008 ] || [ $Year -eq 2012 ]; then
    DaysOfMonth="001 032 061 092 122 153 183 214 245 275 306 336"
    echo "Processing leap year $Year"
    echo "Days of month: $DaysOfMonth"
else DaysOfMonth="001 032 060 091 121 152 182 213 244 274 305 335"
    echo "Processing regular year $Year"
    echo "Days of month: $DaysOfMonth"
fi

for DoY in $DaysOfMonth
do
    # Empty files for VRT lists
    > BA_list.vrt
    > QA_list.vrt

    # Create list of BA VRTs
    for file in $DATADIR/$Year/MCD64A1.A$Year$DoY.h??v??.051.*.hdf
    do
        echo HDF4_EOS:EOS_GRID:"$file":MOD_Grid_Monthly_500m_DB_BA:'"'Burn Date'"' >> BA_list.vrt
        echo HDF4_EOS:EOS_GRID:"$file":MOD_Grid_Monthly_500m_DB_BA:"QA" >> QA_list.vrt
    done

    # Create VRT using the list files
    gdalbuildvrt -input_file_list BA_list.vrt BA.vrt
    gdalbuildvrt -input_file_list QA_list.vrt QA.vrt

    # Reproject the VRT to Lat/Long
    gdalwarp -t_srs 'EPSG:4326' -te -180 -90 180 90 -tr 0.004394531250000 -0.004394531250000 -overwrite -of VRT BA.vrt BA_WGS84.vrt

    gdalwarp -t_srs 'EPSG:4326' -te -180 -90 180 90 -tr 0.004394531250000 -0.004394531250000 -overwrite -of VRT QA.vrt QA_WGS84.vrt

    echo "/usr/bin/python2.7 $SRCDIR/Aggregate.py $DATADIR $Year $Resolution $DoY"
    /usr/bin/python2.7 $SRCDIR/Aggregate.py BA_WGS84.vrt QA_WGS84.vrt $Year $Resolution $DoY

    # rm temporal files
    rm *.vrt
done

