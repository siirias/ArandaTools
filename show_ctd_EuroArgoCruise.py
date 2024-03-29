# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 15:33:34 2020

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
import matplotlib.dates as mdates
import math
import gsw
import warnings
import arandapy as apy
warnings.simplefilter("ignore") #applises some depracating time-axis thing.
C = "sal00"
T = "t090C"
D = "depSM"
#C = "sal00"  # RBR Test
#T = "tnc90C"  # RBR Test
#D = "prM"  # RBR Test
#in_dir = "C:\\Users\\siirias\\Documents\\Aranda2020\\CTD_DATAA\\"
in_dir = "C:\\Data\\EuroArgoCruise\\sbetulos\\"
#in_dir = "D:\\Data\\ArandaVEMIVE2020\\RBRTEST\\"
out_dir = "C:\\Data\\figures\\Aranda\\EuroARgoCruise\\new_shape\\"
out_dir_add = "\\"
close_figures_when_saved = True
colormaps = [
        cmo.cm.deep,    # 0
        cmo.cm.thermal, # 1
        cmo.cm.haline,  # 2
        cmo.cm.gray,    # 3
        cmo.cm.solar,   # 4
        cmo.cm.solar,   # 5
        cmo.cm.gray,    # 6
        cmo.cm.haline,  # 7 
        cmo.cm.dense]   # 8
#variables = [1,4,7,8]
#Parameters:
#0: prDM, Pressure, Digiquartz
#1: t090C, Temperature
#2: c0mS/cm, Conductivity
#3: v0, Voltage 0
#4: sbeox0ML/L, Oxygen, SBE 43
#5: sbeox0PS, Oxygen, SBE 43
#6: nbin, Scans Per Bin
#7: sal00, Salinity, Practical
#8: sigma-é00, Density
#9: depSM, Depth
#10: dm, Dynamic Meters
#11: svCM, Sound Velocity
#12: potemp090C, Potential Temperature
#13: flag, 
#14: Lat, Latitude
#15: Lon, Longitude
#
alpha_val = 0.5
grid_alpha = 0.4
fig_dpi = 300
plot_station_names = True
#highlight = "SBD1"
highlight = None
max_labels = 20
depth_max = None # none = maximum of the data.
#start_ind = 0
#end_ind = -1
#start_ind = 296
#end_ind = 301
filtered_indices = [] # indices listed here are NEVER used. add if something is broken
cruise_year = '21'
plot_sets =[
        ['snit_IU',117,123],
        ['snit_Start',101,109],
#        ['snit_GD',110,116],
        ['snit_I',129,138],
        ['snit_H',139,145],
        ['snit_G',146,152],
        ['snit_F',153, 159],
        ['snit_E',160, 167],
        ['snit_D',168, 175],
        ['snit_C',176, 182],
        ['snit_B',183, 189],
        ['snit_A',190, 196],
        ['snit_G_crop',147,151],
        ['snit_G_new',203,207],
        ['WholeGrid',129,196],
        ['WholeTrip',101,245]
        ]
map_shape = (5,10)
#plot_size = (7,15)
plot_size = (4,8)
JustOne = None
#JustOne = 'snit_Lagsk' #False
#JustOne = 'total' #False
#JustOne = 'RBRTEST' #False
#JustOne = 'SR5' #False
#JustOne = 'SR5_xtra' #False
#JustOne = 'hilasta_eespain' #False
#JustOne = 'hila' #False
#JustOne = 'snit_IU' #False

if(not JustOne): #default values
        map_area = None # None or list: [lat_min,lat_max,lon_min,lon_max]
        #Variable info: variable number, and min max values for plots, or None to both.
        # 1 = T, 4 = O, 7 = S , 8 = D
        variable_info = [[1,7.0,2.0],
                         [4,8.0,4.5],\
                         [7,4.0,8.0],
                         [8,5.3,4.3]]
        axes_to_plot = ['distance'] #'latitude', longitude', 'distance', 'time'
        depth_max = 140.0
else: #Special cse for specific snit
    tmp_plot_set = None
    for i in plot_sets:
        if(i[0] == JustOne):
            plot_sets = [i]
            break;
    if(JustOne == "snit_IU"):
        plot_sets = [['snit_IU',343,350]]
        map_area = None # None or list: [lat_min,lat_max,lon_min,lon_max]
        #Variable info: variable number, and min max values for plots, or None to both.
        variable_info = [[1,None,None],[4,None,None],\
                         [7,None,None],[8,None,None]]
    if(JustOne == "snit_GD"):
        plot_sets = [['snit_GD',110,116]]
        map_area = None # None or list: [lat_min,lat_max,lon_min,lon_max]
        #Variable info: variable number, and min max values for plots, or None to both.
        depth_max = None
        variable_info = [[1,None,None],[4,None,None],\
                         [7,None,None],[8,None,None]]
    if(JustOne == "snit_Lagsk"):
        plot_sets = [['snit_lagsk',[262,351,352,353,354,455,356,357]]]
        map_area = None # None or list: [lat_min,lat_max,lon_min,lon_max]
        #Variable info: variable number, and min max values for plots, or None to both.
        variable_info = [[1,None,None],[4,None,None],\
                         [7,None,None],[8,None,None]]
    if(JustOne == "WholeTrip"):
        plot_sets = [['WholeTrip',101,245]]
        plot_station_names = False
        map_area = None # None or list: [lat_min,lat_max,lon_min,lon_max]
        #Variable info: variable number, and min max values for plots, or None to both.
        axes_to_plot = ['distance', 'time'] #'latitude', longitude', 'distance', 'time'
        depth_max = None
        variable_info = [[1,None,None],[4,None,None],\
                         [7,None,None],[8,None,None]]

#map_shape = None
def sort_by_axis(data, axis):
    new_order = np.argsort(axis)
    result = data.copy()
    for i in new_order:
        result[:,i] = data[:,i]
    return result

def distance(origin, destination): 
    lat1, lon1 = origin 
    lat2, lon2 = destination 
    radius = 6371 # km 
    dlat = math.radians(lat2-lat1) 
    dlon = math.radians(lon2-lon1) 
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c 
    return d

def none_max(values):  #same as np.max, but ignores None values
    val = [x for x in values if x]
    return np.max(val)    
def none_min(values):#same as np.min, but ignores None values
    val = [x for x in values if x]
    return np.min(val)    

for plot_set in plot_sets:
    print(plot_set)
    out_dir_add = plot_set[0]+"\\"
    try:
        os.mkdir(out_dir+out_dir_add)
    except:
        pass # too lazy to find out how to check for dir existence
    if(type(plot_set[1])==int): #define name,start,end
        start_ind = plot_set[1]
        end_ind = plot_set[2]
        if(end_ind<0):
            end_ind = 10000 # big enough that the index number is unlikely exceed
        ok_index_list = list(range(start_ind,end_ind+1))
    if(type(plot_set[1])==list): #define list of indices used
        ok_index_list = plot_set[1]
    in_files = apy.get_aranda_filenames(in_dir, \
                             whitelist = ok_index_list,\
                             blacklist = filtered_indices,\
                             cruise_year = cruise_year)
    number_of_files = len(in_files)
    ctd_datas = []
    file_no = 0
    station_names = []
    station_indices = []
    lats = []
    lons = []
    times = []
    latitude = 60.0
    longitude = 20.0
    for in_file in in_files:
        [data, station_index, station_name, columns, long_names, unit_names] = \
            apy.read_aranda_file(os.path.join(in_dir,in_file))
        station_indices.append(station_index)
        station_names.append(station_name)
        ctd_datas.append(data)

    #plot TS-diagrams
    file_no = 0
    fig = plt.figure(figsize=(10,10))
    default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    min_T = None
    max_T = None
    min_S = None
    max_S = None #these are used to define the limits for the contours
    for ctd_data,station_name,i in zip(ctd_datas,station_names,range(len(ctd_datas))):
        min_T = none_min([min_T,none_min(ctd_data[T])])
        max_T = none_max([max_T,none_max(ctd_data[T])])
        min_S = none_min([min_S,none_min(ctd_data[C])])
        max_S = none_max([max_S,none_max(ctd_data[C])])
        
        color = default_colors[i%len(default_colors)]
        if(len(ctd_datas)>=max_labels):
            color = (1.0-(float(file_no)/len(ctd_datas)),0.0,1.0*(float(file_no)/len(ctd_datas)))
        plt.plot(ctd_data[C], ctd_data[T], zorder = 10,\
                     label = station_name, color = color, marker='.', linestyle = '')
        plt.plot(ctd_data[C], ctd_data[T], zorder = 9,\
                     label = None, color = color, alpha = 0.1)
        file_no +=1
    # Get the fixed limits for T and S, if defined
    for v in variable_info:
        if(v[0] == 1):
            if(v[1]):
                min_T = v[1]
            if(v[2]):
                max_T = v[2]
        if(v[0] == 4):
            if(v[1]):
                min_S = v[1]
            if(v[2]):
                max_S = v[2]
    contour_T = np.linspace(min_T,max_T,128)
    contour_S = np.linspace(min_S,max_S,128)
    x_T,y_C = np.meshgrid(contour_T,contour_S)
    sigma_theta = gsw.sigma0(y_C,x_T)
    cnt = np.linspace(sigma_theta.min(), sigma_theta.max(),156)
    ax = fig.axes[0]
    cs = ax.contour(y_C, x_T, sigma_theta, colors='grey', zorder=1, alpha = 0.5)
    cl=plt.clabel(cs,fontsize=10,inline=True,fmt='%.1f')
    
    if(file_no<=max_labels):
        plt.legend()
    plt.title("{}, from {} to {} ({})".format("TS-Diagram",\
              station_names[0],\
              station_names[-1],\
              plot_set[0]))
    plt.ylabel("{} ({})".format(long_names[1], unit_names[1]))
    plt.xlabel("{} ({})".format(long_names[7], unit_names[7]))
    plt.grid(alpha=grid_alpha)
    filename = "{}_{}_to_{}_profile_cloud.png".format(
            "TS_plot",\
            station_names[0],\
            station_names[-1])
    plt.savefig(out_dir+out_dir_add+filename,\
                        facecolor='w',dpi=fig_dpi,bbox_inches='tight')
    if(close_figures_when_saved):
        plt.close()
            
    
    for var_info in variable_info:
        variable = var_info[0]
        value_min = var_info[1]
        value_max = var_info[2]
        plt.figure(figsize=plot_size)
        try:
            cmap = colormaps[variable]
        except:
            cmap = cmo.cm.gray

        alpha_val_now = alpha_val
        if(highlight and re.match(highlight,station_name)):
            alpha_val_now = 1.0
        file_no = 0
        for ctd_data,station_name in zip(ctd_datas,station_names):
            color = None
            if(len(ctd_datas)>=max_labels):
                color = (1.0-(float(file_no)/len(ctd_datas)),0.0,1.0*(float(file_no)/len(ctd_datas)))
            plt.plot(ctd_data[columns[variable]], ctd_data[D], \
                         label = station_name, color = color, alpha = alpha_val_now)
            file_no +=1
        if(len(ctd_datas)<=max_labels):
            plt.legend()
        plt.gca().invert_yaxis()
        plt.title("{}, from {} to {} ({})".format(long_names[variable],\
                  station_names[0],\
                  station_names[-1],\
                  plot_set[0]))
        plt.ylabel("{} ({})".format(long_names[9], unit_names[9]))
        plt.xlabel("{} ({})".format(long_names[variable], unit_names[variable]))
        plt.grid(alpha=grid_alpha)
        filename = "{}_{}_to_{}_profile_cloud.png".format(
                re.sub("[,\s][,\s]*","_",long_names[variable]),\
                station_names[0],\
                station_names[-1])
        plt.savefig(out_dir+out_dir_add+filename,\
                            facecolor='w',dpi=fig_dpi,bbox_inches='tight')
        if(close_figures_when_saved):
            plt.close()
        #plot the snits in color:
        #first figure out maximum steps in ctd depth
        max_steps = 0
        max_ind = 0
        lat_list = []
        lon_list = []
        time_list = []
        for i in range(len(ctd_datas)):
            lat_list.append(ctd_datas[i]['Lat'][0])
            lon_list.append(ctd_datas[i]['Lon'][0])
            time_list.append(ctd_datas[i]['Time'][0])
            if(len(ctd_datas[i][D])>max_steps):
                max_steps = len(ctd_datas[i][D])
                max_ind = i
        depth_axis = ctd_datas[max_ind][D]
        profile_data = np.zeros((max_steps,len(ctd_datas)));
        profile_data[:,:]=np.NaN
        #create the distance list
        dist_list = [] # first has no distance
        last_lat = lat_list[0]
        last_lon = lon_list[0]
        distance_travelled = 0.0
        for [lat,lon] in zip(lat_list,lon_list):
            dist = distance([lat, lon],[last_lat, last_lon])*0.539956803 # in nautical miles
            distance_travelled += dist
            dist_list.append(distance_travelled)
            last_lat = lat
            last_lon = lon
        for i in range(len(ctd_datas)):
            length = len(ctd_datas[i][columns[variable]])
            profile_data[0:length,i] = ctd_datas[i][columns[variable]]
        axis_list = []
        label_list = []
        if('time' in axes_to_plot):
            axis_list.append(time_list)
            label_list.append("Time")
        if('distance' in axes_to_plot):
            axis_list.append(dist_list)
            label_list.append("Distance (NM)")
        if('latitude' in axes_to_plot):
            axis_list.append(lat_list)
            label_list.append("Latitude")
        if('longitude' in axes_to_plot):
            axis_list.append(lon_list)
            label_list.append("Longitude")
            
        for [x_axis, x_label] in zip(axis_list,label_list):
            arranged_dat = sort_by_axis(profile_data,x_axis)
            sorted_x = np.sort(x_axis)
            if(x_label == "Time"):
                sorted_x = list(map(lambda x:x.to_datetime64(),sorted_x))
            fig = plt.figure(figsize=plot_size)
            plt.pcolormesh(sorted_x, depth_axis, arranged_dat, shading = 'aut', cmap = cmap, alpha = 1.0)
            line_thick = 0.005*(np.max(sorted_x) - np.min(sorted_x))
            if(plot_station_names):
                for i_prof in range(len(sorted_x)):
    #                plt.pcolormesh([sorted_x[i_prof],sorted_x[i_prof]+line_thick],
    #                               depth_axis, 
    #                               arranged_dat[:,[i_prof, i_prof]], shading = 'auto', cmap = cmap)
                    plt.plot([sorted_x[i_prof], sorted_x[i_prof]],
                              [depth_axis[0],list(depth_axis)[-1]], color = 'k', alpha = 0.5)
            if(depth_max is not None):
                plt.ylim(0,depth_max)
            plt.gca().invert_yaxis()
            if(x_label == "Latitude"):
                plt.gca().invert_xaxis()
            if(x_label == "Distance (NM)"):
                lat_diff = lat_list[-1] - lat_list[0] # wanted W->E
                lon_diff = lon_list[0] - lon_list[-1] # Wanted N -> S
                if(np.abs(lon_diff)<np.abs(lat_diff)*3.0): #Magic number for when to move from lon to lat
                    the_diff = lat_diff
                    print("lat diff")
                else:
                    the_diff = lon_diff
                    print("lon diff")
                if(the_diff>0.0): #make sure plot is west->east or North-South
                    plt.gca().invert_xaxis()
                    print("Inverted", the_diff)
            if(plot_station_names):
                for prof_to_name in range(len(x_axis)):
                    plt.text(x_axis[prof_to_name],np.mean(depth_axis),\
                             station_names[prof_to_name], rotation = 90, alpha = 0.4)
                    
#            if(x_label == "Time"):
#                tick_names = list(map(lambda x:x.strftime("%m-%d %H h"),x_axis))
#                the_step = max(1,int(len(x_axis)/10))
#                plt.xticks(x_axis[::the_step],tick_names[::the_step])
#                ax = fig.get_axes()[0]
#                if((x_axis[-1]-x_axis[0]).total_seconds()<2*60*60*24):
#                    ax.xaxis.set_major_locator(mdates.HourLocator())
#                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H h'))
#                else:
#                    ax.xaxis.set_major_locator(mdates.DayLocator())
#                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H h'))
#                    ax.xaxis.set_minor_locator(mdates.HourLocator())
                
            plt.title("{}, from {} to {} ({})".format(long_names[variable],\
                      station_names[0],\
                      station_names[-1],\
                      plot_set[0]))
            plt.ylabel("{} ({})".format(long_names[9], unit_names[9]))
            plt.xlabel("{}".format(x_label))
            plt.xticks(rotation=15)
            plt.grid(alpha=grid_alpha)
            plt.clim(value_min,value_max)
            colorb = plt.colorbar()
            colorb.set_label("{} ({})".format(long_names[variable], unit_names[variable]))
            filename = "{}_{}_to_{}_{}_snit.png".format(
                    re.sub("[,\s][,\s]*","_",long_names[variable]),\
                    station_names[0],\
                    station_names[-1],\
                    re.sub(" .*","",x_label)) # get rid of unit, if in name.
            plt.savefig(out_dir+out_dir_add+filename,\
                                facecolor='w',dpi=fig_dpi,bbox_inches='tight')
            if(close_figures_when_saved):
                plt.close()
                
                
    # plot the map with the points included:
    the_proj = ccrs.PlateCarree()
    fig = plt.figure(figsize=map_shape)
    ax = plt.axes(projection=the_proj)
    if(map_area is not None):
        ax.set_extent(map_area)
        tmp_map_area = map_area  # used to check ranges for texts in map etc.
    else:
        lon_buf = 0.1*(np.max(lon_list) - np.min(lon_list))
        lat_buf = 0.1*(np.max(lat_list) - np.min(lat_list))
        tmp_map_area = [np.min(lon_list)-lon_buf,
                       np.max(lon_list)+lon_buf,
                       np.min(lat_list)-lat_buf,
                       np.max(lat_list)+lon_buf]
        ax.set_extent(tmp_map_area)
    gl = ax.gridlines(crs=the_proj, draw_labels=True,
              linewidth=2, color='gray', alpha=0.3, linestyle='-')
    gl.xlabels_top = False
    gl.ylabels_right = False
    ax.set_aspect('auto')
    ax.coastlines('10m')
    ax.add_feature(cfeature.NaturalEarthFeature('physical', 'land', '10m', edgecolor='face', facecolor='g'))
    plt.plot(lon_list,lat_list,'bo',transform = ccrs.PlateCarree())
    plt.plot(lon_list,lat_list,'b-',transform = ccrs.PlateCarree())
    for [n,lat,lon] in zip(station_names,lat_list,lon_list):
        if(tmp_map_area is not None and \
               lon>tmp_map_area[0] and\
               lon<tmp_map_area[1] and\
               lat>tmp_map_area[2] and\
               lat<tmp_map_area[3]):
            plt.text(lon,lat,n,transform = ccrs.PlateCarree(),alpha=0.5)
    plt.title("{}, from {} to {} ({})".format(long_names[variable],\
              station_names[0],\
              station_names[-1],\
              plot_set[0]))
    filename = "from_{}_to_{}_{}_map.png".format(
            station_names[0],\
            station_names[-1],\
            plot_set[0])
    plt.savefig(out_dir+out_dir_add+filename,\
                        facecolor='w',dpi=fig_dpi,bbox_inches='tight')
    if(close_figures_when_saved):
        plt.close()
            
    #Create the info file
    info_file = open(out_dir+out_dir_add+"info_file_{}.txt".format(plot_set[0]),'w')
    info_file.write("Parameters:\n")
#    print("Variables:")
    for i in range(len(long_names)):
#        print("{}: {}, {}".format(i,columns[i],long_names[i]))
        info_file.write("{}: {}, {}\n".format(i,columns[i],long_names[i]))    
    
    info_file.write("\n\nStations:\n")
    for n,i,f,lat,lon,t in zip(station_names,station_indices,in_files,lat_list,lon_list, times):
        info_file.write("{}:\t{}\t{:.3f}\t{:.3f}\t{}\t{}\n".format(\
                        i,n,lat,lon,f,t.strftime("%Y-%m-%d %H.%M")))
        
    
    
    
    info_file.close()
