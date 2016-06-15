#!/bin/bash

source $HOME/.bashrc

FUNC=MOD09_Masking_By_QA_KernelCalc.sh
echo ""
echo ${FUNC}: Checking command line arguments

if [ $# -ne 2 ]; then
    echo ""
    echo Usage: $FUNC TILE PRODUCT YEAR
    echo To process MOD09 and MYD09 for 2007 for tile h17v03
    echo $FUNC h17v03 2007
    echo ""
    exit 1
fi

init_time=`date`
echo $init_time

tile=$1
year=$2

WORKDIR=`pwd`

SRCDIR=$HOME/MELODIES/src/MODIS/MOD09

# Split the year in 3 0??, 1??, 2??, 3??
product=MOD09GA
for i in `seq 0 3`
do
    echo $SRCDIR/MOD09_Masking_By_QA_KernelCalc.sh $tile $product $year $i
    ( $SRCDIR/MOD09_Masking_By_QA_KernelCalc.sh $tile $product $year $i &> $tile.$product.${year}_${i}.log ) &
done

wait

echo " Started  at $init_time"
echo " Finished at "`date`

