#! /usr/bin/env /usr/bin/python3

'''
@file run_cramer.py
@author Scott L. Williams.
@package ETO_WEATHER
@brief Compare multiple SOMs with each other using Cramer-V similarity measure.
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

# compare multiple SOMs with each other using Cramer-V similarity measure.

run_cramer_copyright = 'run_cramer.py Copyright (c) 2020-2022 Scott L. Williams, released under GNU GPL V3.0'

import os
import sys
import getopt

from cramer import cramer

datafile = 'full2021.npy'
outfile = 'cramer_2021_5x5_5_00725_3.results'

lutdir = 'LUTs_2021_5x5_5_00725_3/'

results = open( outfile, 'w' )

somset = [ './LABELS_2021/5x5_5_00725_3/2021_5x5_5_00725_01.labels',
           './LABELS_2021/5x5_5_00725_3/2021_5x5_5_00725_02.labels',
           './LABELS_2021/5x5_5_00725_3/2021_5x5_5_00725_03.labels',
           './LABELS_2021/5x5_5_00725_3/2021_5x5_5_00725_04.labels',
           './LABELS_2021/5x5_5_00725_3/2021_5x5_5_00725_05.labels',
           './LABELS_2021/5x5_5_00725_3/2021_5x5_5_00725_06.labels',
           './LABELS_2021/5x5_5_00725_3/2021_5x5_5_00725_07.labels',
           './LABELS_2021/5x5_5_00725_3/2021_5x5_5_00725_08.labels',
           './LABELS_2021/5x5_5_00725_3/2021_5x5_5_00725_09.labels',
           './LABELS_2021/5x5_5_00725_3/2021_5x5_5_00725_10.labels' ]
           


# ------------------------------------------------------------------------
nsoms = len(somset)

# check if files exist
for i in range( nsoms ):
    if not os.path.isfile( somset[i]):
        print( 'run_cramer: file:', somset[i], ' does not exist...exiting',
               file=sys.stderr )
        sys.exit( 1 )

if not os.path.isdir( lutdir ):
    os.mkdir( lutdir )
    
# number of combinations
total = 0
for i in range( nsoms ):
    total += i

print( 'comparing', nsoms, 'som mapfiles with each other, for a total of',
       total, ' comparisons.', file=sys.stderr, flush=True )
print( 'results are in the file:', outfile,
       file=sys.stderr, flush=True )

k = 0
for j in range( nsoms ):
    for i in range( j+1, nsoms ):

        print( '\ncomparing: ', somset[j], somset[i],
               file=sys.stderr, flush=True )

        #lutfile = lutdir + str(j+1) + '-' + str(i+1) + '.lut'

        # use train run numbers
        tag1 = somset[j][-9:-7]
        tag2 = somset[i][-9:-7]
        lutfile = lutdir + tag1 + '-' + tag2 + '.lut'

        Cv = cramer( datafile, somset[j], somset[i], lutfile )
        results.write( somset[j] + ' ' +  somset[i] + ' %.4f\n'%Cv )
        results.flush()
        k += 1
        print( 'result for', somset[j], ' ',  somset[i],
               ' -> Cv=%.4f'%Cv, ' %d'%k, 'out of %d'%total,
               file=sys.stderr, flush=True )

results.close()


