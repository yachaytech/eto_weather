#! /usr/bin/env /usr/bin/python3

'''
@file appy_class.py
@author Scott L. Williams.
@package ETO_WEATHER
@brief POLI batch implementation to apply SOM classes to data.
@LICENSE
# 
#  Copyright (C) 2010-2022 Scott L. Williams.
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

#  poli batch implementation to apply SOM classes to data
#  no graphics

apply_class_copyright = 'apply_class.py Copyright (c) 2010-2022 Scott L. Williams, released under GNU GPL V3.0'

import os
import sys
import getopt
import numpy as np

from cnorm_pack import cnorm
from render_pack import render
from prep_eto_pack import prep_eto
from somclass_pack import somclass
from wrf_source_pack import wrf_source

# point to target data files
fname = '/home/agrineer/eto_study/scripts/dates/full2021.txt'
outdir = '2021-GA/SOM_5x5_4_00724_3_10/'
output_file = outdir + '2017-2021_labels.npy'    # labels naming based on SOM training dates

'''
# point to target data files
fname = '/home/agrineer/eto_study/scripts/dates/2017-2021.txt'
outdir = '2017-2021/SOM_5x5_4_00724_3_20/'
output_file = outdir + '2017-2021_labels.npy'    # labels naming based on SOM training dates
'''
# instantiate the operators

src = wrf_source.wrf_source( 'wrf_source' )

prep = prep_eto.prep_eto( 'prep_eto' )
prep.params.albedo = 0.23    # be sure to match this with collect_data.py

cnrm = cnorm.cnorm( 'cnorm' )
cnrm.params.clip = True
cnrm.params.filepath = '2017-2021.coeffs'  # normalization coeffs to use

sclass = somclass.somclass( 'somclass' )
sclass.params.weightfile = 'LABELS_2017-2021/5x5_4_00724_3/2017-2021_5x5_4_00724_10.labels'
sclass.params.nclasses = 25  # match with train grid

# render labels as image
rndr = render.render( 'render' )
rndr.readlut( './luts/eighthbow.lut' )

# --------------------------------------------------------------------------

def print_params(out):
    print( 'dates file   =', fname, file=out )
    print( 'out dir      =', outdir, file=out )
    print( 'numpy labels =', output_file, file=out )
    print( 'coeffs file  =', cnrm.params.filepath, file=out )
    print( 'weights file =', sclass.params.weightfile, file=out, flush=True)
    
# main

# open file with datafile list
datafiles = open( fname )

# check if datafiles exist
for f in datafiles:
    if not os.path.isfile( f.strip() ):
        print( 'apply_class:', f, ' does not exist...exiting',
               file=sys.stderr )
        sys.exit( 1 )
datafiles.seek( 0, 0 )

# find number of days
ndays = len( datafiles.readlines() ) # make sure input file has no trailing '\n'
                                     # TODO: filter file trailing '\n' 
datafiles.seek( 0, 0 )               # reset file pointer to beginning

# output directory for daily class images
if not os.path.isdir( outdir ):
    os.mkdir( outdir )
if not os.path.isdir( outdir + 'IMAGES' ):
    os.mkdir( outdir + 'IMAGES' )      

# report parameters to file and stderr
paramfile = open( outdir + 'params.txt', 'w' )
print_params( paramfile )
paramfile.close()
print_params( sys.stderr )

# create daily class (label) array used for secondary SOM classification
dclass = np.empty( (171,171,ndays), dtype=np.uint8)   # labels are ubytes

nvars = 8 # number of variables in hourly feature space

# template band string; 0-indexed; string 'ts' gets
# replaced with actual hour below
# indicate which bands get extracted from WRF source file
bandstr = 'TSK:ts,EMISS:ts,SWDOWN:ts,GLW:ts,GRDFLX:ts,T2:ts,PSFC:ts,Q2:ts,U10:ts,V10:ts'

# classify and render image to file
k = 0
for f in datafiles:

    f = f.strip()
    print( 'processing ', f, file=sys.stderr )

    # create time augmented numpy array
    # TODO:should discover input dimensions
    aug = np.empty( (171,171,nvars*24), dtype=np.float32 )

    # run through hourly slices to augment feature space
    
    '''
    # use this for one time slice over the day
    # starting at 2:00am Ecuador time, ending 1:00am next day
    # start at 2:00am because time-slice 0 (1:00am) has value
    # issues due to non-spinup
    for i in range(1,25):

        # construct hourly band string, replace 'ts' with time slice value
        src.params.bandstr = bandstr.replace('ts','%02d'%i )
    '''
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
        
        # -------------------------------------------------------
        
        # read the file with specified bands to extract
        src.params.filepath = f
        src.run()

        # process raw variables to get actual input values for Penman-Montieth
        # the operator "prep_eto" does the hourly averaging
        prep.source = src.sink
        prep.run()

        # time slice augmentation of variables
        # implicitely introduces diurnal weather influences over time
        if i == 0:
            aug = prep.sink[:,:,:nvars]
        else:
            aug = np.append( aug, prep.sink[:,:,:nvars], axis=2 )
                         
        print( '.', end='', file=sys.stderr, flush=True )
        
    print( '\n', file=sys.stderr,flush=True )
  
    # normalize with given coefficient file (above)
    cnrm.source = aug
    cnrm.run()

    # classify
    sclass.source = cnrm.sink # use this for normalized data
    #sclass.source = aug      # use this for non-normalized data
                              # comment out normalize code above 

    sclass.run()

    # populate daily classification label array for this day
    dclass[:,:,k] = sclass.sink[:,:,0]
    
    # colorize the labels, write out as jpg; png does not play well with
    # html video tag implementation. (use ffmpeg to animate and force size to
    # by divisible by two.
    # eg. ffmpeg -r 3 -i SOM%4d.jpg -vf scale=256:256  SOM.mp4
    rndr.source = sclass.sink
    rndr.params.filepath = outdir + 'IMAGES/SOM%04d.jpg'%k 
    rndr.run()
    
    k += 1
    
datafiles.close()

# write out daily labels for secondary SOM classification
print( 'writing daily labels file...' + output_file, end='',
       file=sys.stderr, flush=True )

dclass.dump( output_file )
print( ' done', file=sys.stderr, flush=True )
