#! /usr/bin/env /usr/bin/python3

'''
@file collect_data.py
@author Scott L. Williams.
@package ETO_WEATHER
@brief POLI batch implementation to construct a data set for ETo training
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

# constructs a data set for ETo training
# using 24 averaged time-slices on actual variables

collect_data_copyright = 'collect_data.py Copyright (c) 2020-2022 Scott L. Williams, released under GNU GPL V3.0'

import os
import sys
import getopt

import numpy as np

from norm_pack import norm
from append_pack import append
from prep_eto_pack import prep_eto
from wrf_source_pack import wrf_source

# point to data files 
datapath = './dates/jan-mar_2019.txt'  # point to WRF output data
outpath = './jan-mar_2019.npy'

# instantiate the operators
src = wrf_source.wrf_source( 'wrf_source' )

prep = prep_eto.prep_eto( 'prep_eto' )
prep.params.albedo = 0.23

nvars = 8                # number of ETo input actual variables

nrm = norm.norm( 'norm' )
nrm.params.ntype = 0     # 0 for 0 to 1; -1 for -1 to 1 normalization
nrm.params.skip = nvars  # normalization buffer interlace factor
nrm.params.write = True  # write normalization coefficients to file
                         # for later use by cnorm operator
nrm.params.filepath = './jan-mar_2019.coeffs' # output normalization coeffs
                                        
# appends a set of buffers (array) to another set
app = append.append( 'append' ) 

# ----------------------------------------------------------------------------
# main

# augment raw variables with time series 

datafiles = open( datapath )

# check if data files exist
for f in datafiles:
    if not os.path.isfile( f.strip() ):
        print( 'collect_data:', f, ' does not exist...exiting',
               file=sys.stderr )
        sys.exit( 1 )
datafiles.seek( 0, 0 )  # rewind

# NOTE: time slice 11 corresponds to 12:00pm Ecuador time
#       time slice  0 corresponds to 01:00am Ecuador time

# template band string; 0-indexed.
# string 'ts' gets replaced with actual hour below.
# band string indicates which bands get extracted from WRF source file
bandstr = 'TSK:ts,EMISS:ts,SWDOWN:ts,GLW:ts,GRDFLX:ts,T2:ts,PSFC:ts,Q2:ts,U10:ts,V10:ts'

for f in datafiles:
    
    print( 'processing ', f, file=sys.stderr )
    f = f.strip()  # remove white spaces

    # run through hourly slices to augment feature space

    # read two slices and average actual values over the day
    # NOTE: should be using spin-up values  
    for i in range(0,24):

        # construct wrf_source band string, replace 'ts' with first time slice value
        bstr = bandstr.replace('ts','%02d'%i )
        
        # second time slice is added to string          
        # if operator "prep_eto" sees 10 bands it will implement directly
        # if operator "prep_eto" sees 20 bands it will implement two sets
        # and return an average
        
        # tell the source operator to get both time slices        
        src.params.bandstr = bstr + ',' + bandstr.replace('ts','%02d'%(i+1) )

        # read the file with specifird bands (above) to extract
        src.params.filepath = f
        src.run()

        # process raw variables to get actual input values for Penman-Montieth
        prep.source = src.sink
        prep.run()
                                              
        # time slice variable augmentation to feature space
        # implicitly introduces diurnal weather influences over time
        if i == 0: # value needs to be same as start i
            aug = prep.sink
        else:
            aug = np.append( aug, prep.sink, axis=2 )
                         
        ''' same thing done manually                
        for j in range( nvars ):
            aug[:,:,((i-1)*nvars + j)] = prep.sink[:,:,j]
        '''
        print( '.', end='', file=sys.stderr, flush=True )

    print( '\n', file=sys.stderr, flush=True )
    
    # link augmented output to append operator input and run
    # to get daily series
    app.source = aug
    app.run()

datafiles.close()

# use line below for non-normalized data; comment out normalization below
#app.sink.dump( outpath )

#''' Normalize entire span of data (hourly and daily)
print( 'normalizing...', file=sys.stderr, flush=True, end='' )
nrm.source = app.sink # link append output to normalize input and run
nrm.run()
print( 'done', file=sys.stderr, flush=True )

# save as numpy file
print( 'writing to file...', file=sys.stderr, flush=True, end='' )
nrm.sink.dump( outpath, protocol=4 )
print( 'done', file=sys.stderr, flush=True )

'''
# get max and min values for each variable and its position
# just to validate spread 0 to 1, or -1 to 1
# TODO: implement interlace

from numpy import unravel_index

# reports first one encountered
for i in range( nvar ):

    maxx = nrm.sink[:,:,i].max()
    index = nrm.sink[:,:,i].argmax()
    max_index = unravel_index( index, nrm.sink[:,:,i].shape) 
    print( i, maxx, max_index )
    
    minn = nrm.sink[:,:,i].min()
    index = nrm.sink[:,:,i].argmin()
    min_index = unravel_index( index, nrm.sink[:,:,i].shape) 
    print( i, minn, min_index,'\n' )
''' 
