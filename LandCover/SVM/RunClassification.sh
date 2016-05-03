#!/bin/bash

year=$1

DATADIR=$HOME/MELODIES/data/MODIS/processing/mosaics
# Input features
#b1 - VIS
#b2 - NIR
#b3 - SWIR
band1=$DATADIR/$year/interpolated/$year.f0.b1.interpolated.vrt
band2=$DATADIR/$year/interpolated/$year.f0.b2.interpolated.vrt
band5=$DATADIR/$year/interpolated/$year.f0.b5.interpolated.vrt
band7=$DATADIR/$year/interpolated/$year.f0.b7.interpolated.vrt
DEM=$HOME/MELODIES/data/ASTER_Global_DEM_V2/ASTER_Global_DEM_V2_mosaic_normalized.tif
Slope=$HOME/MELODIES/data/ASTER_Global_DEM_V2/ASTER_Global_DEM_V2_mosaic_SlopePercent.tif

# Samples
samples=$HOME/MELODIES/data/LandCover/LCM/LandCoverMap_2007_25m_raster/data/resampled/samples/SamplesFromFractions.img

mask=$HOME/MELODIES/data/LandCover/LCM/LandCoverMap_2007_25m_raster/data/resampled/LCC_maxprob.tif

version=B2_B5_NDVI_DEM_Slope_ts_interpolated_${year}_wings_pure_pixels_window
#version=B2_B5_B7_NDVI_Slope_ts_interpolated_${year}_wings_pure_pixels_window
WORKDIR=$DATADIR/Classification/$year/$version

mkdir -p $WORKDIR
cd $WORKDIR

# Create symlink from trained SVM from base year (2007) to the working directory
base_year=2007
base_version=B2_B5_NDVI_DEM_Slope_ts_interpolated_${base_year}_wings_pure_pixels_window
ln -sf $DATADIR/Classification/$base_year/$base_version/MELODIES_SVM_clf.pkl* .

# run classifier
SRCDIR=$HOME/MELODIES/src/LandCover/SVM

#echo "python $SRCDIR/SVM_subset_B2_B5_NDVI_DEM.py \
#       $band1 $band2 $band5 $DEM $samples MELODIES_SVM_clf.pkl"
#python $SRCDIR/SVM_subset_B2_B5_NDVI_DEM.py \
#       $band1 $band2 $band5 $DEM $samples MELODIES_SVM_clf.pkl

echo "python $SRCDIR/SVM_subset_B2_B5_NDVI_DEM_Slope.py \
       $band1 $band2 $band5 $DEM $Slope $samples $mask MELODIES_SVM_clf.pkl"
python $SRCDIR/SVM_subset_B2_B5_NDVI_DEM_Slope.py \
       $band1 $band2 $band5 $DEM $Slope $samples $mask MELODIES_SVM_clf.pkl

