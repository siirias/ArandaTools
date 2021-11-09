# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 10:31:40 2020

@author: siirias
"""

import sys
import os
import re
import pandas as pd
import matplotlib as mp
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import cmocean as cmo
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import matplotlib.dates as mdates
import math
import gsw
out_dir = "C:\\Data\\figures\\aranda2021\\"
##Original 
#out_filename = "map_pickup_zone.png"
#map_area = [17.5,22.0,56.6,58.5]
#pick_up_lims = ((19.7, 20.4),(57.05, 57.5))
#pick_up_center = (np.mean(pick_up_lims[0]), np.mean(pick_up_lims[1]))
#pickup_width = np.abs(np.diff(pick_up_lims)[0])*1.1
#pickup_height = np.abs(np.diff(pick_up_lims)[1])*1.1
plot_set = 'GotlandDeep2021' #['GotlandDeep','NorthernProper']
lon_list = None
lat_list = None
#Circle
out_filename = "map_pickup_zone_rectangle.png"
map_area = [17.5,22.0,56.6,58.5]
pick_up_lims = ((19.635, 20.468),(57.05, 57.5))
pick_up_center = (np.mean(pick_up_lims[0]), np.mean(pick_up_lims[1]))
pickup_width = np.abs(np.diff(pick_up_lims)[0])*1.1
pickup_height = np.abs(np.diff(pick_up_lims)[1])*1.1

if(plot_set == 'GotlandDeep'):
    points = [(57.3170,20.0355,'BY15'), (57.35, 19.93,'Dep')]  
    map_area = [17.5,22.0,56.6,58.5]
    pickup_lims = ((19.5,20.2),(59.0,59.3))
    out_filename = "map_pickup_zone_GD.png"
if(plot_set == 'GotlandDeep2021'):
    points = [(57.3170,20.0355,'BY15')]  
    map_area = [17.5,22.0,56.6,58.5]
    pickup_lims = ((19.5,20.2),(59.0,59.3))
    out_filename = "map_pickup_zone_GD.png"
if(plot_set == 'NorthernProper'):
    points = []  
    map_area = [18.1,23.0,58.5,60.0]
    pickup_corner1 = (19.5,58.8 )
    pickup_corner2 = (20.4, 59.3 )
    pickup_w = pickup_corner2[0]-pickup_corner1[0]
    pickup_h = pickup_corner2[1]-pickup_corner1[1]
    out_filename = "map_argo_BPN.png"

the_proj = ccrs.PlateCarree()
fig = plt.figure(figsize=(15,10))
ax = plt.axes(projection=the_proj)
if(map_area is not None):
    ax.set_extent(map_area)
else:
    ax.set_extent([np.min(lon_list),np.max(lon_list),np.min(lat_list),np.max(lat_list)])
gl = ax.gridlines(crs=the_proj, draw_labels=True,
          linewidth=2, color='gray', alpha=0.3, linestyle='-')
gl.xlabels_top = False
gl.ylabels_right = False
ax.set_aspect('auto')
ax.coastlines('10m')
ax.add_feature(cfeature.NaturalEarthFeature('physical', 'land', '10m',\
                                         edgecolor='face', facecolor='#555570'))
# #ax.add_feature(cfeature.NaturalEarthFeature('cultural', 'admin_0_pacific_groupings', '10m',edgecolor='black',facecolor = 'none'))
# ax.add_feature(cfeature.NaturalEarthFeature('cultural', 'admin_0_boundary_lines_land', '10m',edgecolor='black',facecolor = 'none',alpha = 0.1))

EEZ = ShapelyFeature(Reader("C:\\Data\\Layers\\Intersect_EEZ_IHO_v4_2020\\Intersect_EEZ_IHO_v4_2020.shp").geometries(),
                                the_proj, edgecolor='blue', facecolor = 'none', linewidth = 3.0, alpha = 0.3)
ax.add_feature(EEZ)

#pick_up_area = mp.patches.Ellipse(pick_up_center, pickup_width, pickup_height,\
#                                  color = "#55aa55", alpha = 0.3)
#
if(plot_set == 'GotlandDeep' or plot_set == 'GotlandDeep2021'):
    pick_up_area = mp.patches.Rectangle((19.6,57),20.5-19.6,57.5-57.0,\
                                      color = "#55aa00", alpha = 0.3)
if(plot_set == 'NorthernProper'):
    pick_up_area = mp.patches.Rectangle(pickup_corner1,pickup_w,pickup_h,\
                                      color = "#ff0000", alpha = 0.3)
                                           
ax.add_artist(pick_up_area)                                      
#plt.plot(lon_list,lat_list,'bo',transform = ccrs.PlateCarree())
#plt.plot(lon_list,lat_list,'b-',transform = ccrs.PlateCarree())
for [lat,lon,n] in points:
        plt.text(lon,lat,n,transform = ccrs.PlateCarree(),alpha=0.5)
        plt.plot([lon],[lat],'.',color='b')
#plt.title("{}, from {} to {} ({})".format(long_names[variable],\
#          station_names[0],\
#          station_names[-1],\
#          plot_set[0]))
#filename = "from_{}_to_{}_{}_map.png".format(
#        station_names[0],\
#        station_names[-1],\
#        plot_set[0])
plt.savefig(out_dir+out_filename,\
                    facecolor='w', dpi=300, bbox_inches='tight')
