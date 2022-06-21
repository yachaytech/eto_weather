#! /usr/bin/env /usr/bin/python3

'''
@file plot_buffers.py
@author Scott L. Williams.
@package ETO_WEATHER
@brief Render flattened data buffers.
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

# render flattened data buffers

plot_buffers_copyright = 'plot_buffers.py Copyright (c) 2020-2022 Scott L. Williams, released under GNU GPL V3.0'

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# force axis size since i can't get it to self-adjust
ax.set_xlim3d(-10, 180)
ax.set_ylim3d(-10, 180)
ax.set_zlim3d(-10, 160)

x = [0,170,170,0]
y = [0,0,170,170]

colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple','tab:brown','tab:pink', 'tab:grey']

for i in range(8):
    z = [i*20,i*20,i*20,i*20]
    verts = [list(zip(x,y,z))]
    ax.add_collection3d( Poly3DCollection(verts, facecolors=colors[i],alpha=0.7 ) )

ax.set_xlabel( 'X' )
ax.set_ylabel( 'Y' )
ax.set_zlabel( '\n\n\nActual ETo variables',linespacing=2 )

ax.set_yticks( [0,20,40,60,80,100,120,140,160,180] )
ax.set_xticks( [180,160,140,120,100,80,60,40,20,0] )

bands = ['Rn', 'G' ,'T', 'D', 'g', 'es', 'ea', 'u2']

ax.set_zticks( [0,20,40,60,80,100,120,140,160] )
ax.set_zticklabels( bands,rotation = 45, ha="right" ) 

plt.title( 'ETo Variable Buffers' )
plt.show()

