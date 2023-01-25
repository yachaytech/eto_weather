#! /usr/bin/env /usr/bin/python3

#  latlon2grid.py
# 
#  Copyright (C) 2022 Scott L. Williams.
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

# read a geo_em file and create a full grid shapefile

copyright = 'latlon2grid.py Copyright (c) 2022 Scott L. Williams ' + \
            'released under GNU GPL V3.0'

import os
import ogr
import sys
import getopt

import math
import numpy as np
from osgeo import osr
from netCDF4 import Dataset

# make a grid shapefile from images of lat,lon
class latlon2grid():
    def __init__( self, infile, outshpfile ):

        # check for infile 
        if not os.path.isfile( infile ):
            raise RuntimeError( 'input file ' + infile + ' does not exist')

        self.infile_path = infile
        outfile_path = outshpfile

        # set up shapefile stuff
        driver = ogr.GetDriverByName( 'Esri Shapefile' )
        
        # for unknown reasons ds has to be self.ds, it is not used elsewhere
        # if not self.ds then segments in ogr.Feature( self.defn ) below
        self.ds = driver.CreateDataSource( outfile_path )

        srs = osr.SpatialReference()
        result = srs.ImportFromEPSG( 4326 ) 
        if result != 0:
            raise RuntimeError(repr(res) + ': could not import from EPSG')

        # TODO: make layer name variable
        self.layer = self.ds.CreateLayer( 'sectors', srs, ogr.wkbLineString )

        # add ID attribute
        self.layer.CreateField( ogr.FieldDefn('id', ogr.OFTInteger) )

        # add name attribute
        self.layer.CreateField( ogr.FieldDefn('name', ogr.OFTString) )
        
        self.defn = self.layer.GetLayerDefn()

    # end __init__

    def asRadians( self, degrees ):
        return degrees*math.pi/180
    
    def offset_lon( self, lat, lon, meters ):
        alat = abs(lat)
        latitude_circumference = 40075160 * math.cos( self.asRadians(alat) ) # in meters
        ratio = meters/latitude_circumference
        return lon + ratio*360
    
    def offset_lat( self, lat, lon, meters ):
        longitude_circumference = 40008000 # in meters
        ratio = meters/longitude_circumference
        return lat + ratio*360
        
    # make perimeter grid points
    def ll2perim_grid( self, in_path ):

        datas = Dataset( in_path, 'r' )     # origin is bottom left corner
        
        # get distances in meters
        dx = datas.getncattr('DX')
        dy = datas.getncattr('DY')

        # leave this for later development
        if dx != dy:
            print( 'dx and dy distances do not match' )
            exit(1)
            
        latvar = datas.variables['XLAT_M']  # reduce dimensionality
        latbuf = latvar[0,:,:]              # time,y,x
                                            # location of cell centers
        lonvar = datas.variables['XLONG_M']
        lonbuf = lonvar[0,:,:]

        # not likely but check anyway
        if lonbuf.shape != latbuf.shape:
            raise RuntimeError( 'latlon2poly: lat and lon dimensions do not match' )

        numy = latbuf.shape[0]
        numx = latbuf.shape[1]

        offset = dx/2  # half the cell distance
        
        # construct grid arrays
        
        glat = np.zeros( (numy+1,numx+1), dtype=np.float64 )
        glon = np.zeros( (numy+1,numx+1), dtype=np.float64 )

        # populate grid arrays by shifting given points south and west
        # brute force; there are probably more elegant ways
        for j in range(numy):
            for i in range(numx):
                glat[j,i] = self.offset_lat( latbuf[j,i], lonbuf[j,i], -offset )
                glon[j,i] = self.offset_lon( latbuf[j,i], lonbuf[j,i], -offset )

        # fill in last (top) row
        for i in range(numx):
            glat[numy,i] = self.offset_lat( latbuf[numy-1,i],
                                            lonbuf[numy-1,i], offset )
            glon[numy,i] = self.offset_lon( latbuf[numy-1,i],
                                            lonbuf[numy-1,i], -offset )

        # fill in last (right) column
        for j in range(numy):
            glat[j,numx] = self.offset_lat( latbuf[j,numx-1],
                                            lonbuf[j,numx-1], -offset )
            glon[j,numx] = self.offset_lon( latbuf[j,numx-1],
                                            lonbuf[j,numx-1], offset )

        # and top right corner
        glat[numy,numx] = self.offset_lat( latbuf[numy-1,numx-1],
                                           lonbuf[numy-1,numx-1], offset )
        glon[numy,numx] = self.offset_lon( latbuf[numy-1,numx-1],
                                           lonbuf[numy-1,numx-1], offset )

        return glat, glon

    # end ll2perim_grid

    def cellLine( self, coords ):
        line = ogr.Geometry( type=ogr.wkbLineString )
        for xy in coords:
            line.AddPoint_2D( xy[0], xy[1] )
        return line

    # read WRF geo data file for lat, lon and make shapefile
    def ll2grid( self, shape_id, name, infile_path ):

        # check for infile 
        if not os.path.isfile( infile_path ):
            raise RuntimeError( 'input file ' + infile_path + 
                                ' does not exist')

        print( 'working on:', infile_path, file=sys.stderr )

        # read center lat,lon grid and make a prerimeter grid
        glat,glon = self.ll2perim_grid( infile_path )

        # create a new feature (attributes and geometry)

        # lay down attributes
        feat = ogr.Feature( self.defn )
        feat.SetField( 'id', shape_id )
        feat.SetField( 'name', name )

        numy = glat.shape[0]
        numx = glat.shape[1]

        # horizontal lines
        for j in range(numy):
            for i in range(numx-1):
                line = self.cellLine( [ (glon[j,i],   glat[j,i]),
                                        (glon[j,i+1], glat[j,i+1]) ] )
                feat.SetGeometry( line )
            
                # set the feature
                self.layer.CreateFeature( feat )

        # vertical lines
        for i in range(numx):
            for j in range(numy-1):
                line = self.cellLine( [ (glon[j,i],   glat[j,i]),
                                        (glon[j+1,i], glat[j+1,i]) ] )
                feat.SetGeometry( line )
            
                # set the feature
                self.layer.CreateFeature( feat )

    # end ll2grid
                
    # read wrf buffers and generate shapefile
    def read_and_run( self ):

        f = open( self.infile_path, 'r' )
        
        # parse input file
        i = 0
        for line in f:
            line.strip()   # remove white spaces
            items = line.split( ',' )
            self.ll2grid( i, items[0], items[1].rstrip() )
            i += 1

        f.close()
        
    # end read_and_run

# end class latlon2grid

# ------------------------------------------------------------------

def usage():
    print( 'usage: latlon2grid.py', file=sys.stderr )
    print( '       -h, --help', file=sys.stderr )
    print( '       -i geofile, --input=geofiles.csv', file=sys.stderr )
    print( '       -o shpfile, --output=shpfile.shp', file=sys.stderr )
    pass
            
def set_params( argv ):
    infile = None   # CSV file
    outfile = None

    try:                                
        opts, args = getopt.getopt( argv, 'hi:o:', 
                                        ['help','input=','output='] )
    except getopt.GetoptError:           
        usage()                          
        sys.exit(2)  
                   
    for opt, arg in opts:                
        if opt in ( '-h', '--help' ):      
            usage()                     
            sys.exit(0)   

        elif opt in ( '-i', '--input' ):    
            infile = arg

        elif opt in ( '-o', '--output' ):
            outfile = arg   # should include .shp suffix

    if infile == None or outfile == None:
        print( 'latlon2grid.py: must specify i/o files', file=sys.stderr )
        sys.exit(2)

    return infile, outfile

if __name__ == '__main__':  
    infile, outfile = set_params( sys.argv[1:] )
    oper = latlon2grid( infile, outfile )
    oper.read_and_run()                  

# end latlon2grid.py
