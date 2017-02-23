__author__ = 'Jane'
import subprocess
import gdal_vrtmerge
import os
import sys

print gdal_vrtmerge.__file__
the_path = os.path.dirname(gdal_vrtmerge.__file__)


try:
    subprocess.check_call('python ' + the_path + os.path.sep + 'gdal_vrtmerge.py -o input.vrt -separate output.vrt')
except subprocess.CalledProcessError as err:
    print ('err msgs: ' + err.cmd)
    print '\n'
    os.system("gdal_translate -of VRT ")