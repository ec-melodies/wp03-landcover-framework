#!/bin/bash

Year=$1

for DoY in `seq 152 365`
do
	echo $DoY
	strDoY=`echo $DoY | awk '{ if (length($1)==1) printf("00%d", $1); else if (length($1)==2) printf("0%d", $1); else printf("%d", $1)}'`
	echo "lynx -dump ftp://ladsftp.nascom.nasa.gov/allData/5/MYD021KM/$Year/$strDoY | cut -d/ -f4-9 >> 2011"
	lynx -dump ftp://ladsftp.nascom.nasa.gov/allData/5/MYD021KM/$Year/$strDoY | cut -d/ -f4-9 > tmp
	cat tmp | grep allData | grep hdf > tmp1
	cat tmp1 | awk -F. '{ if ($3>=1200 && $3 <= 1500) print $0}' >> $Year
	rm tmp tmp1
done
