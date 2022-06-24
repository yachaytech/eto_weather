#! /usr/bin/env /usr/bin/python3

'''
@file cramer.py
@author Scott L. Williams.
@package ETO_WEATHER
@brief POLI batch implementation to compare two SOMs using a modified Cramer-V similarity measure.
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

# compare two SOMs using a modified Cramer-V similaririty measure

cramer_copyright = 'cramer.py Copyright (c) 2020-2022 Scott L. Williams, released under GNU GPL V3.0'

import os
import sys
import getopt
import math
import numpy as np

from npy_source_pack import npy_source

# -------------------------------------------------------------

# read a som file for weights
def readsom( somfile ):

    wfile = open( somfile, 'r' ) 

    print( 'reading ', somfile, file=sys.stderr)
    
    # print header and look for flag
    found = False
    for line in wfile:
        if line.find( 'NEURONS' ) != -1:
            found = True
            break
        print( line.strip(), file=sys.stderr )
                
    if not found:
        print( 'cramer:could not find flag...exiting', file=sys.stderr )
        sys.exit( 1 )
                
    nneurons,ndim = wfile.readline().split()
    nneurons = int( nneurons )
    ndim = int( ndim )

    # get the neuron weights
    
    # allocate buffer
    neurons = np.empty( (nneurons,ndim), dtype=np.float32 )

    # retrieve neurons from file
    for i in range( nneurons):            
        line = wfile.readline().split()    # get line components:
        
        for j in range( 1, ndim+1 ):       # skip grey level label
            neurons[i,j-1] = float( line[j] )
            
    wfile.close()

    return neurons

def find_BMU( num, neurons, sample ):

    # just find the closest vector

    # initialize
    diff = sample - neurons[0]
    diff = np.abs( diff )
    min_dist = np.sum( diff, axis=0 )
    label = 0
    
    for i in range(1,num):
        diff = sample - neurons[i]
        diff = np.abs( diff )
        tmp = np.sum( diff, axis=0 )
        if tmp < min_dist:
            min_dist = tmp
            label = i

    return label

def cramer( datafile, som1file, som2file, lutfile ):
    
    # get the soms
    som1 = readsom( som1file )
    som2 = readsom( som2file )

    # check dimensions
    if som1.shape != som2.shape:
        print( 'cramer: som maps do have same shape...exiting' )
        sys.exit( 1 )
    
    # get the training data
    src = npy_source.npy_source( 'npy_source' )
    src.params.filepath = datafile

    print( 'reading datafile: ' + src.params.filepath + '...',
           file=sys.stderr, flush=True, end='' )
    src.run()
    print( 'done', file=sys.stderr, flush=True )

    data = src.sink
    ny,nx,ndim = data.shape

    # check if vector dimensions match
    nlabels, ndim_som = som1.shape
    ny, nx, ndim_data = data.shape
    if ndim_som != ndim_data:
        print( 'cramer: vector dimensions are mismatched...exiting',
               file=sys.stderr )
        sys.exit( 2 )

    # allocate observable matrix and set to zero
    obs = [[0 for i in range(nlabels)] for j in range(nlabels)]

    # construct observable matrix
    print( 'constructing observable matrix...',
           file=sys.stderr, end='', flush=True )

    # assign first SOM to be columns (x), second SOM to be rows (y)
    for j in range( ny ):
        for i in range( nx ):
            label1 = find_BMU( nlabels, som1, data[j,i,:] )
            label2 = find_BMU( nlabels, som2, data[j,i,:] )
            obs[label2][label1] += 1

    print( 'done', file=sys.stderr, flush=True )

    '''
    for j in range( nlabels ):
        print( obs[j], file=sys.stderr, flush=True )
    '''

    # create a class to class mapping (LUT) SOM1 labels to SOM2 labels
    # for later application in similarity measures
    if lutfile != None:
        print( 'creating lut...', file=sys.stderr, flush=True, end='')

        lut = [0 for i in range( nlabels ) ]
        
        # brute force
        for i in range( nlabels ):
            
            # find maximum for this column
            maxc = -math.inf
            for j in range( nlabels ):
                if obs[j][i] > maxc:
                    maxc = obs[j][i]
                    ij = j
            lut[i] = ij

        lfile = open( lutfile, 'w' )
        for i in range( nlabels-1 ):
            lfile.write( str(lut[i]) + ',' )
        lfile.write( str(lut[i+1]) + '\n' )
        lfile.close()

        print( 'done', file=sys.stderr, flush=True )
            
    # construct vectors/matrices
    Ni = [0 for i in range(nlabels)]
    for i in range(nlabels):
        Ni[i] = 0
        for j in range(nlabels):
            Ni[i] += obs[j][i]
        
        if Ni[i] == 0:
            print( 'cramer: error...Ni element at', i, ' is zero' )
            print( 'an unused label is indicated in file ' + som1file )
            print( 'try reducing number of classes in training...exiting.' )
            sys.exit(0)
        
    # get sum of vector
    sum_ni = 0
    for i in range(nlabels):
        sum_ni += Ni[i]

    Nj = [0 for i in range(nlabels)]
    for j in range(nlabels):
        Nj[j] = 0
        for i in range(nlabels):
            Nj[j] += obs[j][i]
        
        if Nj[j] == 0:
            print( 'cramer: error...Nj element at', i, ' is zero' )
            print( 'an unused label is indicated in file ' + som2file )
            print( 'try reducing number of classes in training...exiting.' )
            sys.exit(0)

    # get sum of vector
    sum_nj = 0
    for j in range(nlabels):
        sum_nj += Nj[j]

    if sum_nj != sum_ni:
        print( 'cramer: sums do not match...exiting', file=sys.stderr )
        sys.exit( 1 )

    ntotal = nx*ny    # total number of pixels

    if sum_nj != ntotal:
        print( 'cramer: sample sums do not match...exiting', file=sys.stderr )
        sys.exit( 1 )

    # calculate expected values
    expected = [[0 for i in range(nlabels)] for j in range(nlabels)]
    for j in range( nlabels ):
        for i in range( nlabels ):
            expected[j][i] = (Nj[j] * Ni[i])/ntotal

    # calculate chi squared
    chisq = [[0 for i in range(nlabels)] for j in range(nlabels)]
    for j in range( nlabels ):
        for i in range( nlabels ):
            chisq[j][i] = ((obs[j][i]-expected[j][i])**2)/expected[j][i]

    # calculate cramer-v

    # numerator
    sum_chisq = 0.0
    for j in range( nlabels ):
        for i in range( nlabels ):
            sum_chisq += chisq[j][i]

    # denominator
    denominator = ntotal*(nlabels-1)

    Cv = math.sqrt( sum_chisq/denominator )
    print( 'cramer-v done', file=sys.stderr, flush=True )

    return Cv


#----------------------------------------------------------

def usage( self ):
        print( 'usage: cramer.py', file=sys.stderr )
        print( '       -h, --help', file=sys.stderr )
        print( '       -d datafile --data=datafile', file=sys.stderr )
        print( '       -f somfile, --first=somfile',file=sys.stderr )
        print( '       -s somfile, --second=somfile',file=sys.stderr )
        print( '       -l lutfile, --lut=lutfile',file=sys.stderr )

def get_params( argv ):
    datafile = None
    som1file = None
    som2file = None
    lutfile = None
        
    try:                                
        opts, args = getopt.getopt( argv, 'hd:f:s:l:',
                                    ['help','data=','first=','second=','lut='] )
            
    except getopt.GetoptError:           
        self.usage()                          
        sys.exit(2)  
                   
    for opt, arg in opts:                
        if opt in ( '-h', '--help' ):      
            self.usage()                     
            sys.exit(0)
        elif opt in ( '-d', '--data' ):
            datafile = arg
        elif opt in ( '-f', '--first' ):
            som1file = arg
        elif opt in ( '-s', '--second' ):
            som2file = arg
        elif opt in ( '-l', '--lut' ):
            lutfile = arg
        else:
            self.usage()                     
            sys.exit(1)

    if datafile == None:
        print( 'cramer: datafile is missing...exiting' )
        sys.exit(1)
    if som1file == None:
        print( 'cramer: first somfile is missing...exiting' )
        sys.exit(1)
    if som2file == None:
        print( 'cramer: second somfile is missing...exiting' )
        sys.exit(1)

    return datafile, som1file, som2file, lutfile

####################################################################
# command line user entry point 
####################################################################
if __name__ == '__main__':  

    dataf,som1f,som2f,lutf = get_params( sys.argv[1:] )

    Cv = cramer( dataf, som1f, som2f, lutf )
    print( 'Cramer value =', Cv )
