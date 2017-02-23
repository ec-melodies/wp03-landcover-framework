#!/bin/bash

source $HOME/.bashrc

echo $#

FUNC=ProcessMOD09.sh
echo ""
echo ${FUNC}: Checking command line arguments

#if [ $# -ne 2 ] & [ $# -ne 4 ] ; then
if [ $# -ne 4 ] ; then
    echo ""
    echo Usage: $FUNC TILE PRODUCT YEAR
    echo To process MOD09 and MYD09 for 2007 for tile h17v03
    echo $FUNC h17v03 2007
    echo ""
    echo To process MOD09 and MYD09 for DoY 300 2007 onwards for tile h17v03
    # this doesn't make sense...
    echo $FUNC h17v03 2007 3 3
    exit 1
fi

# get datetime at the start of this process
init_time=`date`
echo $init_time

tile=$1 #arg1
year=$2 #arg2
# sections of the year to process
init_day=$3
end_year=$4  # should be end_day_of_year

if [ $# -gt 2 ]; then
    init_day=$3
    end_year=$4
else
    init_day=0
    end_year=3 #really?
fi

WORKDIR=`pwd`

SRCDIR=$HOME/MELODIES/src/MODIS/MOD09 # this will have to change

# Split the year in 4: 0??, 1??, 2??, 3??
product=MOD09GA
for i in `seq $init_day $end_year`
do
    # run the script with args: tile, product, year, each day/year in sequence
	echo $SRCDIR/MOD09_Masking_By_QA_KernelCalc.sh $tile $product $year $i
	( $SRCDIR/MOD09_Masking_By_QA_KernelCalc.sh $tile $product $year $i  &> $tile.$product.${year}_${i}.log ) &
done

product=MYD09GA
for i in `seq $init_day $end_year`
do
    echo $SRCDIR/MOD09_Masking_By_QA_KernelCalc.sh $tile $product $year $i
    ( $SRCDIR/MOD09_Masking_By_QA_KernelCalc.sh $tile $product $year $i &> $tile.$product.${year}_${i}.log ) &
done

wait

# Print out time taken
echo " Started  at $init_time"
echo " Finished at "`date`

