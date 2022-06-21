#! /usr/bin/env /usr/bin/python3

'''
@file train_msom.py
@author Scott L. Williams.
@package ETO_WEATHER
@brief #  POLI batch implementation to train SOM and writes out labels
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
#  poli batch implementation to train SOM and writes out labels

train_minisom_copyright = 'train_msom.py Copyright (c) 2020-2022 Scott L. Williams, released under GNU GPL V3.0'

import os
import sys
import getopt

from npy_source_pack import npy_source
from msom_pack import msom

# instantiate the operators

# numpy source

src = npy_source.npy_source( 'npy_source' )
src.params.filepath = './jan-mar_2019.npy'  # data to train on

# mini-som
ms = msom.msom( 'msom' )
ms.params.shape = (5,5)              # neural net grid shape
ms.params.sigma = 2.5                
                                      
ms.params.nepochs = 3                # number of epochs. an epoch
                                     # is a full sampling of the data.
                                     # multiples epochs allow for pixel
                                     # reconsideration and node reassignment
                                      
ms.params.rate = 0.00724             # learning rate
ms.params.show_progress = False

ms.params.init_weights = 'pca'
ms.params.neighborhood_function = 'gaussian'
ms.params.topology = 'hexagonal'      
ms.params.activation_distance = 'euclidean' 
ms.params.output_type = 'labels'
ms.params.mapfile_prefix = 'jan-mar_2019_5x5_3_00724_01'
ms.params.apply_classification = False
ms.params.rorder = True              # sample at random
ms.params.seed = None                # None means generate a seed.
                                     # no fair assigning one
ms.params.decay_function = 3         # inverse decay function
#------------------------------------------------------------

# print the (partial) parameters
print( 'number of epochs=', ms.params.nepochs, file=sys.stderr, flush=True )
print( 'learning rate=   ', ms.params.rate, file=sys.stderr, flush=True )
print( 'prefix=          ', ms.params.mapfile_prefix, file=sys.stderr, flush=True )

# read the training data
print( 'reading datafile: ' + src.params.filepath + '...',
       file=sys.stderr, flush=True, end='' )
src.run()
print( 'done', file=sys.stderr, flush=True )

# link src output to msom input and run
print( 'training ...', file=sys.stderr, flush=True )
ms.source = src.sink
ms.run() # train
print( 'training done', file=sys.stderr, flush=True )
