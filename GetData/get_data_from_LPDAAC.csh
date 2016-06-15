#!/bin/csh

set FUNC = get_data_from_LPDAAC.csh

if ($#argv != 4) then
  echo ""
  echo Usage: $FUNC PRODUCT YEAR TILE STARTING_DOY
  echo "PRODUCT must be the MODIS shortname product, check: https://lpdaac.usgs.gov/dataset_discovery/modis/modis_products_table"
  echo "To get the MODIS-Terra daily surface reflectance product for the whole year 2011 for tile h18v04:"
  echo "$FUNC MOD09GA 2011 h18v04 1"
  echo "To get  the same data  but from DoY 46:"
  echo "$FUNC MOD09GA 2011 h18v04 46"
  echo ""
  exit 1
endif

set SCRIPTS_DIR = $HOME/MELODIES/src/GetData

set product = $1
set year = $2
set tile = $3
set StartingDoY = $4

set julian_day = $StartingDoY
set collection = "005"

set prefix = `echo $product | cut -c1-3`
if ($prefix == "MOD") then
  set datadir = "MOLT"
  set TemporalResolution = 1
else if ($prefix == "MYD") then
  set datadir = "MOLA"
  set TemporalResolution = 1
else
  # For combined products there is no daily data
  set datadir = "MOTA"
  set TemporalResolution = 8
endif

while ( $julian_day <= 365)

  #Check if files already exists
  while ( $status == 0)
    set julian_day_three_chars = `echo $julian_day | awk '{if (length($1)==1) $1="00"$1; else if (length($1)==2) $1="0"$1} {print $1}'`
    test -e $product.A${year}${julian_day_three_chars}.${tile}.$collection*hdf
    #test -e BROWSE.$product.A${year}${julian_day_three_chars}.${tile}.$collection*jpg
    if ( $status == 0 ) then
      @ julian_day = $julian_day + $TemporalResolution
    else
      break
    endif
  end

  set image_date = `$SCRIPTS_DIR/convert_julian_day_to_gregorian_date.csh $julian_day $year`
  echo $datadir/$product.$collection/$image_date

  echo "lynx -dump http://e4ftl01.cr.usgs.gov/$datadir/$product.$collection/$image_date/"
  lynx -dump http://e4ftl01.cr.usgs.gov/$datadir/$product.$collection/$image_date/ > tmp.txt
  cat tmp.txt | grep $tile | grep http | grep .hdf | awk '{print $2}' > ToDownload.txt

  set NumberOfFiles = `cat  ToDownload.txt | wc -l`
  if ( $NumberOfFiles >= 1 ) then

    wget -i ToDownload.txt -nc

    test -e $product.A${year}*${julian_day}.${tile}.$collection*hdf
    #test -e BROWSE.$product.A${year}*${julian_day}.${tile}.$collection*jpg
    if ( $status == 0 ) then
      @ julian_day = $julian_day + $TemporalResolution
    endif

  else
    # There is no data for this DoY/Tile
    @ julian_day = $julian_day + $TemporalResolution
  endif

end
