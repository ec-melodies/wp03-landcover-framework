#!/bin/bash

source $HOME/.bashrc

init_time=`date`

SRCDIR=$HOME/MELODIES/src/MODIS/MOD09

DATADIR=$1 # e.g. /home/dn907640/MELODIES/data/MODIS
           # local storage /local/MELODIES/data/MODIS
tile=$2

year=$3
previous_year=`echo $year - 1 | bc`
following_year=`echo $year + 1 | bc`

snow=$4

# Create local directory structure
LocalDir=$DATADIR/$tile/MOD09GA/VRTs
mkdir -p $LocalDir
cp $HOME/MELODIES/data/MODIS/$tile/MOD09GA/VRTs/MOD09GA.${year}???.$tile.*tif $LocalDir
cp $HOME/MELODIES/data/MODIS/$tile/MOD09GA/VRTs/MOD09GA.${previous_year}3??.$tile.*tif $LocalDir
cp $HOME/MELODIES/data/MODIS/$tile/MOD09GA/VRTs/MOD09GA.${following_year}0??.$tile.*tif $LocalDir

LocalDir=$DATADIR/$tile/MYD09GA/VRTs
mkdir -p $LocalDir
cp $HOME/MELODIES/data/MODIS/$tile/MYD09GA/VRTs/MYD09GA.${year}???.$tile.*tif $LocalDir
cp $HOME/MELODIES/data/MODIS/$tile/MYD09GA/VRTs/MYD09GA.${previous_year}3??.$tile.*tif $LocalDir
cp $HOME/MELODIES/data/MODIS/$tile/MYD09GA/VRTs/MYD09GA.${following_year}0??.$tile.*tif $LocalDir

if [ $snow -eq 0 ]; then
	OUTDIR=$HOME/MELODIES/data/MODIS/processing/$tile/NoSnow
else
	OUTDIR=$HOME/MELODIES/data/MODIS/processing/$tile/Snow
fi
cd $OUTDIR

# Doulapa has 12 cores, use only 11 to leave some room for some OS stuff
# If you feel naughty and want to use all cores, set NumberOfProcesses=12
NumberOfProcesses=7 # zero-based
#NumberOfProcesses=1

i=1
for DoY in `seq 201 8 365`
#for DoY in 241 289 305 313 321 329 337 345 353 361
do
	strDoY=`echo $DoY | awk '{ if (length($1)==1) printf("00%d", $1); else if (length($1)==2) printf("0%d", $1); else printf("%d", $1)}'`
	if [ $i -le $NumberOfProcesses ]; then
		echo $SRCDIR/BRDF_Inverter.py $strDoY $DATADIR $year $tile $snow
		$SRCDIR/BRDF_Inverter.py $strDoY $DATADIR $year $tile $snow &> $tile.$year$strDoY.log &
		# Renice process to highest priority
		#sudo renice -n  -20 `ps -ef | grep python | awk '{print $2}'`
		sleep 30s
		#sleep 10s
		if [ $i -eq $NumberOfProcesses ]; then
			echo "Wating for any job to finish..."
			KeepWaiting=1
			while [ $KeepWaiting -eq 1 ]; do 
		        running=$(jobs | wc -l)
		        if [ $running -ge $NumberOfProcesses ]; then
        	        # echo "$(date +%T)|still $running running... sleeping"
            	    sleep 1
		        else
        	        echo "$(date +%T) | only $running running now..."
					KeepWaiting=0
		        fi
			done

			let i=$i-1
		else
			let i=$i+1
		fi
	fi
done

# All processes must be finished
wait

echo "$init_time - `date`"
