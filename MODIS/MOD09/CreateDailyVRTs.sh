#!/bin/bash

DATADIR=$1
# e.g. /home/dn907640/MELODIES/data/MODIS

Year=$2

Product=MOD09GA

WORKDIR=$DATADIR/$$
mkdir $WORKDIR
cd $WORKDIR

# Create VRT's for all MODIS 7 refl bands
for DoY in `seq 1 8 365`
do
	for band in `seq 1 7`
	do
		BandsToMosaic=""
		for tile in h17v03 h17v04 h18v03
		do
			strDoY=`echo $DoY | awk '{ if (length($1)==1) printf("00%d", $1); else if (length($1)==2) printf("0%d", $1); else printf("%d", $1)}'`

			# Create tmp VRTs of files to mosaic
            gdal_translate -of VRT -b $band \
                 $DATADIR/$tile/$product/VRTs/$Product.$Year$strDoY.$tile.tif \
                 $Product.$Year$strDoY.$tile.b$band.vrt

            BandsToMosaic="$BandsToMosaic $Year$strDoY.$tile.b$band.vrt"
		done

		# Create virtal mosaic for each band
		gdalbuildvrt $Product.$Year$strDoY.b$band.full.vrt $BandsToMosaic

		gdalwarp -of VRT -t_srs '+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs ' -te -759832.86 5532417.15 161696.14 6671703.12 -tr 463.312719959778804 -463.312716551443543 $Product.$Year$strDoY.b$band.full.vrt $Product.$Year$strDoY.b$band.vrt

		exit

	done
done

# Create layerstacks
for band in `seq 1 7`
do
	gdal_vrtmerge.py -o $Product.$Year.b$band.vrt -separate $Product.$Year???.b$band.vrt
done

# Move results to output dir
mkdir -p $DATADIR/mosaics
mv *.vrt  $DATADIR/mosaics
