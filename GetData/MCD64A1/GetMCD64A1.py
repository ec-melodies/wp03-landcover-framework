#!/usr/bin/env python

import sys
import os
import calendar
import logging
import time
import ftplib
import subprocess

__author__ = "Gerardo Lopez-Saldana (UREAD)"
__copyright__ = "(c) 2014"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "G Lopez-Saldana"
__email__ = "G.LopezSaldana@reading.ac.uk"
__status__ = "Development"

# Log file
LOG = logging.getLogger( __name__ )

def GetStrDoY(DoY):
    """Returns DoY as string
    """
    if len(str(int(DoY))) == 1:
        strDoY = '00' + str(int(DoY))
    elif len(str(int(DoY))) == 2:
        strDoY = '0' + str(int(DoY))
    else:
        strDoY = str(int(DoY))

    return strDoY

def humansize(nbytes):
    """Human-friendly fire sizes!"""
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

def get_mcd64a1( tile, year, output_dir ):
    """Downloads the MCD45 product, collection 5.1 from ftp://fuoco.geog.umd.edu
    Function requires a tile, a year and an output directory. It returns
    a list with the successfully downloaded files (full path). No checks
    are made, so the user should ideally test that the data are actually
    OK.

    Parameters
    ----------
    tile: str
        A MODIS tile reference (e.g. h17v04)
    year: int
        A year (2000 to 2013)
    output_dir: str
        An output directory where files will be stored.
    """

    if not os.path.exists ( os.path.join ( output_dir, "MCD64A1" ) ):
        os.mkdir ( os.path.join ( output_dir, "MCD64A1" ) )
    
    #import pdb; pdb.set_trace()
    doys = calendar.mdays[:-1]
    doys[0] = doys[0] + 1
    if calendar.isleap(year):
        doys[2] += 1
    
    # now add the temporal wings... for 45 days we need two months...
    ### actually not sure if we need wings for these products??? or only 09 prods?
    #import pdb; pdb.set_trace()
    doys = [sum(doys[:i+1]) for i in range(len(doys))] 
    dload_file_list = {}
    session = ftplib.FTP( 'fuoco.geog.umd.edu', 'fire', 'burnt' )

    product = "MCD64A1"
    session.cwd ( "/db/" + product  +"/" + tile )
    file_list = []
    session.retrlines('LIST', file_list.append)
    dload_file_list[product] = []
    
    for doy in doys:
        for individual_file in file_list:
            #import pdb; pdb.set_trace()
            if individual_file.find('A' + str(year) + GetStrDoY(doy)) >= 0:
                fname = individual_file.split ()[-1].strip()
                remote_size = int( individual_file.split ()[4] )
                download = True
                if os.path.exists ( os.path.join (  output_dir, "MCD64A1", fname)   ):
                    local_size = os.path.getsize( os.path.join ( \
                        output_dir, "MCD64A1", fname)  )
                    if local_size != remote_size:
                        os.remove ( os.path.join ( output_dir, "MCD64A1", fname) )
                        download = True
                    else:
                        LOG.info ("Skipping %s", fname )
                        download = False
                if download:
                    LOG.info ( "Downloading %s",  fname )
                    dload_fname = os.path.join ( output_dir, "MCD64A1", fname)
                    while True:
                        tic = time.time()
                        try:
                            with open(dload_fname, "wb") as fp:
                                session.retrbinary("RETR " + fname, fp.write)
                                dload_file_list[product].append ( dload_fname)
                            toc = time.time()
                            LOG.info ("\t Done! Downloaded %s in %d s" %  \
                                ( humansize ( remote_size ), toc-tic ) )
                        except ftplib.error_temp:
                            os.remove ( dload_fname )
                            time.sleep(20)
                            continue
                        break
                    

    return dload_file_list

 
if __name__ == "__main__":

    # Parse the input arguments
    if len ( sys.argv ) <> 4:
        print "Usage:"
        print "python GetMCD64A1.py TILE YEAR OUTDIR"
        print "   for instance:"
        print "   python GetMCD64A1.py h19v07 2011 /home/glopez/MODIS"
        exit()
    else:
        tile = sys.argv[1]
        year = int ( sys.argv[2] )
        outdir = sys.argv[3]

        get_mcd64a1 ( tile, year, outdir )

