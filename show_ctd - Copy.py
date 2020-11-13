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
import warnings
warnings.simplefilter("ignore") #applises some depracating time-axis thing.

in_dir = "C:\\Users\\siirias\\Documents\\Aranda2020\\CTD_DATAA\\"
out_dir = "D:\\Data\\figures\\Aranda\\"
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
#Variable info: variable number, and min max values for plots, or None to both.
variable_info = [[1,3.0,13.0],[4,3.0,9.0],\
                 [7,4.0,7.0],[8,4.0,6.0]]
variable_info = [[1,None,None],[4,None,None],\
                 [7,None,None],[8,None,None]]
alpha_val = 0.5
fig_dpi = 300
#highlight = "SBD1"
highlight = None
max_labels = 20
#start_ind = 0
#end_ind = -1
start_ind = 296
end_ind = 301
plot_sets =[
        ['',0,-1],
        ['snit_1',[289,290,301,302,313,314]],
        ['snit_2',[288,291,300,303,312,315]],
        ['snit_3',[287,292,299,304,311,316]],
        ['snit_4',[286,293,298,305,310,318]],
        ['snit_5',[285,294,297,306,309,319]],
        ['snit_6',[284,295,296,307,308,320]],
        ['aland_snit',260,278],
        ['aland_1',[262,263,264,265,272,273,274,275,276,277,278]],
        ['aland_2',265,269],
        ['north_aland',279,282],
        ['border_snit',283,289],
        ['snit_a',290,295],
        ['snit_b',296,301],
        ['snit_c',302,307],
        ['snit_d',308,313],
        ['snit_e',314,320],
        ['hila',289,320]
        ]
plot_sets = [['',0,-1]]
map_area = None # None or list: [lat_min,lat_max,lon_min,lon_max]
#map_area = [18.5,21.0,59.7,61.4]
map_shape = (5,10)
map_shape = None
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
    in_files_tmp = os.listdir(in_dir)  # all files
    in_files_tmp = [i for i in in_files_tmp if re.match(".*a\.cnv", i)] # right types
    # then separate with index
    in_files = []
    for i in in_files_tmp:
        index_no = int(re.search(".*(\d\d\d\d)a\.cnv",i).groups()[0])
#        if( index_no >= start_ind and (end_ind<0 or index_no<=end_ind)):
        if( index_no in ok_index_list):
            in_files.append(i)
    number_of_files = len(in_files)
    
    def sort_by_axis(data, axis):
        new_order = np.argsort(axis)
        result = data.copy()
        for i in new_order:
            result[:,i] = data[:,i]
        return result
    
    for var_info in variable_info:
        variable = var_info[0]
        value_min = var_info[1]
        value_max = var_info[2]
        try:
            cmap = colormaps[variable]
        except:
            cmap = cmo.cm.gray
        ctd_datas = []
        file_no = 0
        plt.figure(figsize=(7,15))
        station_names = []
        station_indices = []
        lats = []
        lons = []
        times = []
        for in_file in in_files:
            lines = open(in_dir+in_file,'r').readlines()
            end_found = False  #search end to find start of data
            data = []
            columns = []
            long_names = []
            unit_names = []
            for l in lines:
                #search for the headers
                if(re.match("# name \d?",l)):
                    try:
                        index = re.search("# name (\d?)",l).groups()[0].strip()
                    except:
                        index = None
                    try:
                        name = re.search("# name \d?.*=([^:]*)",l).groups()[0].strip()
                    except:
                        name = None
                    try:
                        long_name = re.search("# name \d?.*=[^:]*:([^\[]*)",l).groups()[0].strip()
                    except:
                        long_name = ""
                    try:
                        unit_name = re.search("# name \d?.*\[(.*)\]",l).groups()[0].strip()
                    except:
                        unit_name = ""
                    columns.append(name)                  
                    long_names.append(long_name)                  
                    unit_names.append(unit_name)                  
                # search other than column metadata
                if(re.match("\*\* Station name",l)):
                    try:
                        station_name = re.search("\*\* Station name.*:(.*)",l).groups()[0].strip()
                    except:
                        station_name = "?"
                    station_names.append(station_name)
    
                if(re.match("\*\* Index",l)):
                    try:
                        station_index = int(re.search("\*\* Index.*:(.*)",l).groups()[0].strip())
                    except:
                        station_index = 0
                    station_indices.append(station_index)
                    
                
                if(re.match("\*\* Latitude",l)):
                    try:
                        latitude = re.search("\*\* Latitude.*:(.*)",l).groups()[0].strip()
                        latitude = float(re.search("(\d*) \d",latitude).groups()[0]) +\
                                   float(re.search("\d* ([\d\.]*)",latitude).groups()[0])/60.0 
                    except:
                        latitude = 0.0
                    lats.append(latitude)
                if(re.match("\*\* Longitude",l)):
                    try:
                        longitude = re.search("\*\* Longitude.*:(.*)",l).groups()[0].strip()
                        longitude = float(re.search("(\d*) \d",longitude).groups()[0]) +\
                                   float(re.search("\d* ([\d\.]*)",longitude).groups()[0])/60.0 
                    except:
                        longitude = 0.0
                    lons.append(longitude)
    
                if(re.match("\*\* Date and time",l)):
                    try:
                        the_time = re.search("\*\*.*:(.*)",l).groups()[0].strip()
                        the_time = re.sub(",","",the_time)
                        the_time = dt.datetime.strptime(the_time,"%d.%m.%Y %H.%M")
                    except:
                        the_time = dt.datetime(2000,1,1)
                    times.append(the_time)
    
                if(end_found):
                    l_t = re.sub("\s\s*"," ",l.strip()).split(" ")
                    l_t = list(map(lambda x: float(x),l_t))
                    l_t.append(latitude)
                    l_t.append(longitude)
                    data.append(l_t)
                if(re.match('\*END\*',l)):
                    end_found = True
            columns.append('Lat')
            columns.append('Lon')
            long_names.append('Latitude')
            long_names.append('Longitude')
            ctd_data = pd.DataFrame(data,columns = columns)
            ctd_datas.append(ctd_data)
            color = (1.0-(float(file_no)/number_of_files),0.0,(float(file_no)/number_of_files))
            color = None
            alpha_val_now = alpha_val
            if(highlight and re.match(highlight,station_name)):
                alpha_val_now = 1.0
            plt.plot(ctd_data[columns[variable]], ctd_data['prDM'], \
                         label = station_name, color = color, alpha = alpha_val_now)
            file_no +=1
        if(file_no<=max_labels):
            plt.legend()
        plt.gca().invert_yaxis()
        plt.title("{}, from {} to {} ({})".format(long_names[variable],\
                  station_names[0],\
                  station_names[-1],\
                  plot_set[0]))
        plt.ylabel("{} ({})".format(long_names[0], unit_names[0]))
        plt.xlabel("{} ({})".format(long_names[variable], unit_names[variable]))
        plt.grid()
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
        for i in range(len(ctd_datas)):
            lat_list.append(ctd_datas[i]['Lat'][0])
            lon_list.append(ctd_datas[i]['Lon'][0])
            if(len(ctd_datas[i]['prDM'])>max_steps):
                max_steps = len(ctd_datas[i]['prDM'])
                max_ind = i
        depth_axis = ctd_datas[max_ind]['prDM']
        profile_data = np.zeros((max_steps,len(ctd_datas)));
        profile_data[:,:]=np.NaN
        for i in range(len(ctd_datas)):
            length = len(ctd_datas[i][columns[variable]])
            profile_data[0:length,i] = ctd_datas[i][columns[variable]]
        for [x_axis, x_label] in zip([times, lat_list, lon_list],["Time","Latitude","Longitude"]):
            arranged_dat = sort_by_axis(profile_data,x_axis)
            fig = plt.figure(figsize=(15,7))
            plt.pcolormesh(x_axis, depth_axis, arranged_dat, shading = 'auto', cmap = cmap)
            plt.gca().invert_yaxis()
            if(x_label == "Latitude"):
                plt.gca().invert_xaxis()
                
            plt.title("{}, from {} to {} ({})".format(long_names[variable],\
                      station_names[0],\
                      station_names[-1],\
                      plot_set[0]))
            plt.ylabel("{} ({})".format(long_names[0], unit_names[0]))
            plt.xlabel("{}".format(x_label))
            plt.xticks(rotation=15)
            plt.grid()
            plt.clim(value_min,value_max)
            colorb = plt.colorbar()
            colorb.set_label("{} ({})".format(long_names[variable], unit_names[variable]))
            filename = "{}_{}_to_{}_{}_snit.png".format(
                    re.sub("[,\s][,\s]*","_",long_names[variable]),\
                    station_names[0],\
                    station_names[-1],\
                    x_label)
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
        else:
            ax.set_extent([np.min(lon_list),np.max(lon_list),np.min(lat_list),np.max(lat_list)])
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
            if(map_area is not None and \
                   lon>map_area[0] and\
                   lon<map_area[1] and\
                   lat>map_area[2] and\
                   lat<map_area[3]):
                plt.text(lon,lat,n,transform = ccrs.PlateCarree(),alpha=0.5)
        plt.title("{}, from {} to {} ({})".format(long_names[variable],\
                  station_names[0],\
                  station_names[-1],\
                  plot_set[0]))
        filename = "from_{}_to_{}_{}_map.png".format(
                station_names[0],\
                station_names[-1],\
                x_label)
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
        info_file.write("{}:\t{}\t{:.3f}\t{:.3f}\t{}\n".format(\
                        i,n,lat,lon,f,t.strftime("%Y-%m-%d %H.%M")))
        
    
    
    
    info_file.close()
