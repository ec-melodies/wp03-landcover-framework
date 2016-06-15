#!/bin/bash

DATADIR=$1
# e.g. /home/dn907640/MELODIES/data/MODIS/processing

Year=$2

WORKDIR=$DATADIR/$$
mkdir $WORKDIR
cd $WORKDIR

tiles="h17v03 h17v04 h18v03"

# Create VRT's for all MODIS 7 refl bands
for DoY in `seq 1 8 365`
do
	strDoY=`echo $DoY | awk '{ if (length($1)==1) printf("00%d", $1); else if (length($1)==2) printf("0%d", $1); else printf("%d", $1)}'`
	# If at least one of the file exist continue with the processing
	FileExist=0
    for file in $DATADIR/h??v??/NoSnow/BRDF_Parameters.$Year$strDoY.h??v??.img
	do
		if [ -e $file ] 
		then
			FileExist=1
		fi
	done
	if [ $FileExist -eq 0 ]
	then
		continue
	fi

	# Create the mosaics for each band
	echo "Processing mosaics for DoY $strDoY..."
	for band in `seq 1 7`
	do
		BandsToMosaic=""
		for tile in $tiles
		do
			# Create tmp VRTs of files to mosaic
            BandToExtract=`echo ${band}*3-2 | bc`
	        gdal_translate -of VRT -b $BandToExtract \
                 $DATADIR/$tile/NoSnow/BRDF_Parameters.$Year$strDoY.$tile.img \
                 $Year$strDoY.$tile.b$band.vrt

            BandsToMosaic="$BandsToMosaic $Year$strDoY.$tile.b$band.vrt"
		done

		# Create virtal mosaic for each band
		gdalbuildvrt $Year$strDoY.f0.b$band.full.vrt $BandsToMosaic

		gdalwarp -of VRT -t_srs '+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs ' -te -759832.86 5532417.15 161696.14 6671703.12 -tr 463.312719959778804 -463.312716551443543 $Year$strDoY.f0.b$band.full.vrt $Year$strDoY.f0.b$band.vrt

	done
done

# Create layerstacks
for band in `seq 1 7`
do
	gdal_vrtmerge.py -o $Year.f0.b$band.vrt -separate $Year???.f0.b$band.vrt
done

# Move results to output dir
mkdir -p $DATADIR/mosaics/$Year
mv *.vrt  $DATADIR/mosaics/$Year

# -----------------------------------
# Create VRT's for NSamples - band 43
# -----------------------------------
for DoY in `seq 1 8 365`
do
	strDoY=`echo $DoY | awk '{ if (length($1)==1) printf("00%d", $1); else if (length($1)==2) printf("0%d", $1); else printf("%d", $1)}'`
    # If at least one of the file exist continue with the processing
    FileExist=0
    for file in $DATADIR/h??v??/NoSnow/BRDF_Parameters.$Year$strDoY.h??v??.img
    do
        if [ -e $file ]
        then
            FileExist=1
        fi
    done
    if [ $FileExist -eq 0 ]
    then
        continue
    fi

	BandsToMosaic=""
	for tile in h17v03 h17v04 h18v03
	do
		strDoY=`echo $DoY | awk '{ if (length($1)==1) printf("00%d", $1); else if (length($1)==2) printf("0%d", $1); else printf("%d", $1)}'`

		# Create tmp VRTs of files to mosaic
		BandToExtract=43
		gdal_translate -of VRT -b $BandToExtract \
			$DATADIR/$tile/NoSnow/BRDF_Parameters.$Year$strDoY.$tile.img \
			$Year$strDoY.$tile.NSamples.vrt

		BandsToMosaic="$BandsToMosaic $Year$strDoY.$tile.NSamples.vrt"
	done

	# Create virtal mosaic for each band
	gdalbuildvrt $Year$strDoY.NSamples.full.vrt $BandsToMosaic

	gdalwarp -of VRT -t_srs '+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs ' -te -759832.86 5532417.15 161696.14 6671703.12 -tr 463.312719959778804 -463.312716551443543 $Year$strDoY.NSamples.full.vrt $Year$strDoY.NSamples.vrt

done

# Create a NSamples layerstack
gdal_vrtmerge.py -o $Year.NSamples.vrt -separate $Year???.NSamples.vrt

mv *.vrt  $DATADIR/mosaics/$Year

# ------------------------------------------
# Create VRT's for Goodness of fit - band 45
# ------------------------------------------
for DoY in `seq 1 8 365`
do
	strDoY=`echo $DoY | awk '{ if (length($1)==1) printf("00%d", $1); else if (length($1)==2) printf("0%d", $1); else printf("%d", $1)}'`
    # If at least one of the file exist continue with the processing
    FileExist=0
    for file in $DATADIR/h??v??/NoSnow/BRDF_Parameters.$Year$strDoY.h??v??.img
    do
        if [ -e $file ]
        then
            FileExist=1
        fi
    done
    if [ $FileExist -eq 0 ]
    then
        continue
    fi

    BandsToMosaic=""
    for tile in h17v03 h17v04 h18v03
    do
        strDoY=`echo $DoY | awk '{ if (length($1)==1) printf("00%d", $1); else if (length($1)==2) printf("0%d", $1); else printf("%d", $1)}'`

        # Create tmp VRTs of files to mosaic
        BandToExtract=45
        gdal_translate -of VRT -b $BandToExtract \
            $DATADIR/$tile/NoSnow/BRDF_Parameters.$Year$strDoY.$tile.img \
            $Year$strDoY.$tile.GoF.vrt

        BandsToMosaic="$BandsToMosaic $Year$strDoY.$tile.GoF.vrt"
    done

    # Create virtal mosaic for each band
    gdalbuildvrt $Year$strDoY.GoF.full.vrt $BandsToMosaic

    gdalwarp -of VRT -t_srs '+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs ' -te -759832.86 5532417.15 161696.14 6671703.12 -tr 463.312719959778804 -463.312716551443543 $Year$strDoY.GoF.full.vrt $Year$strDoY.GoF.vrt

done

# Create a NSamples layerstack
gdal_vrtmerge.py -o $Year.GoF.vrt -separate $Year???.GoF.vrt

mv *.vrt  $DATADIR/mosaics/$Year
