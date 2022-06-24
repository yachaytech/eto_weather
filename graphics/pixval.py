#! /usr/bin/env /usr/bin/python3

'''
@file pixval.py
@author Scott L. Williams.
@package ETO_WEATHER
@brief Retrieve a specified pixel's band values from a numpy file and write out the values to a text csv file.
@LICENSE
# 
#  Copyright (C) 2020-2022 Scott L. Williams.
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
'''
# retrieve a specified pixel's band values from a numpy file
# and write out the values to a text csv file.

pixval_copyright = 'pixval.py Copyright (c) 2020-2022 Scott L. Williams, released under GNU GPL V3.0'

import os
import sys

from npy_source_pack import npy_source

# list pixels to sample (numpy arrays have origin at top left)
# format used is x,y
pixels = [ [0,0],           
           [30,0],
           [60,0],
           [90,0],
           [120,0],
           [150,0] ]

# TODO: make these parameters
dirpath = './'
inpath = dirpath + 'jan-mar_2019.npy'
outpath = dirpath + 'jan-mar_2019.csv'

# ----------------------------------------------------------------

# instantiate the numpy source operator
src = npy_source.npy_source( 'npy_source' )
src.params.filepath = inpath 

# output file
out = open( outpath, 'w' )
out.write( inpath + '\n' ) # report numpy file

src.run()   # read the numpy data

# get dimensions
height,width,nbands = src.sink.shape

for i in range( len(pixels) ):
    x = pixels[i][0]
    y = pixels[i][1]

    # check if specified pixel is inside numpy array
    if y < 0 or y >= height:
        print( 'pixel: ', i, ' has out of range y value: ', y )
        continue

    # check if specified pixel is inside numpy array
    if x < 0 or x >= width:
        print( 'pixel: ', i, ' has out of range x value: ', x )
        continue
    
    # report pixel position to file as x,y
    out.write( str(x) +',' + str(y) + ',' )

    # retrieve the specified pixel's data
    bands = src.sink[y,x,:] # numpy uses y,x format

    # write out values 
    for j in range( nbands-1 ):
        out.write( str(bands[j]) + ',' )
    
    out.write( str(bands[nbands-1]) + '\n' )
        
out.close()
           


