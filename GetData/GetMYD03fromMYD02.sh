#!/bin/bash

Year=$1

DATADIR=/home/dn907640/MELODIES/data/MODIS/MYD02/$Year

echo "#!/bin/bash" >> MYD03.$Year

echo 'ftp -n << EOF' >> MYD03.$Year
echo "open ladsftp.nascom.nasa.gov" >> MYD03.$Year
echo "user anonymous g.lopezsaldana@reading.ac.uk" >> MYD03.$Year
echo "bin" >> MYD03.$Year

for file in $DATADIR/*hdf
do
	date=`basename $file | cut -d. -f2-3`
	MYD03_file=`cat /home/dn907640/MELODIES/data/MODIS/MYD03/$Year/$Year | grep $date`
	echo get $MYD03_file `basename $MYD03_file` >> MYD03.$Year
done

echo "close" >> MYD03.$Year
echo "bye" >> MYD03.$Year
echo "EOF" >> MYD03.$Year

