#! /usr/bin/env /usr/bin/python3

'''
@file plot_pixels.py
@author Scott L. Williams.
@package ETO_WEATHER
@brief Plot selected pixel values as bars.
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
# plot selected pixel values as bars.

plot_pixels_copyright = 'plot_pixels.py Copyright (c) 2010-2022 Scott L. Williams, released under GNU GPL V3.0'

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# define hours of interest
start = 11*8                 # 12 noon      ( 1 hour )
end = start + 1*8

#start = 9*8                  # 10am - 2pm
#end = start + 4*8

#start = 0                     # all day
#end = start + 24*8


# first read the sample file
infile = open( 'jan-mar_2019.csv' )

# ------------------------------------------------------------------------

srcfile = infile.readline()              # get source filename

values = []                              # array of variable value arrays
xpixpos = []                             # array of sampled pixel x positions
for line in infile:
    
    items = line.split( ',' )            # parse out values from text line
    xpixpos.append( int( items[0] ) )    # grab pixel x position
    
    varvalues = []                       # array of variable values 
    for i in range(2,len(items)):      
        varvalues.append( float(items[i].strip()) )

    values.append( varvalues[::-1] )     # reverse order of values to make
                                         # graph more intiutive when rotated

# set up plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# lengths colors has to match number of samples
colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple','tab:brown','tab:pink', 'tab:grey' ]

for i in range( len(values) ):

    # plot the bar graph 
    xs = range( len(values[i][start:end]) )
    ax.bar( xs, values[i][start:end],  zs=xpixpos[i], zdir='y',
            color=colors[::-1], alpha=0.7)

ax.set_xlabel('\nETo actual variables',linespacing=1)
ax.set_ylabel('\nPixel X position\nY=0',linespacing=1)
ax.set_zlabel('\nNormalized ETo Variable value',linespacing=1)

# band labels
bands = ['Rn', 'G', 'T', 'D', 'g', 'es', 'ea', 'u2']

# NOTE: band labels should be used only on the single hour.
#       gets messy otherwise
if end-start == 8:
    
    # must be done before tick label
    ax.set_xticks( range( len(values[0][start:end]) ) )
    ax.set_xticklabels( bands[::-1] ) # prints out band labels
else:
    ax.set_xticklabels( [] )          # prints empty tick marks; hours > 1

#plt.title( 'Source file: ' + srcfile )
plt.show()
