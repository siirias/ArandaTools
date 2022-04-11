# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 15:33:34 2020
gathers the CTD data from original files and plots a set of figures.

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
warnings.simplefilter("ignore") #applises some depracating time-axis thing.
C = "sal00"
T = "t090C"
D = "prDM"
#C = "sal00"  # RBR Test
#T = "tnc90C"  # RBR Test
#D = "prM"  # RBR Test
#in_dir = "C:\\Users\\siirias\\Documents\\Aranda2020\\CTD_DATAA\\"
#in_dir = "D:\\Data\\ArandaVEMIVE2020\\"
#in_dir = "C:\\Users\\siirias\\Documents\\Aranda2022\\DATA\\"
in_dir = "C:\\Users\\siirias\\Documents\\Aranda2022\\usb-tikku\\aranda\\matka02\\ctddata\\data\\"
#in_dir = "D:\\Data\\ArandaVEMIVE2020\\RBRTEST\\"
out_dir = "c:\\Data\\figures\\Aranda\\cable1\\"
out_dir_add = "\\"
weatherdata_file = "C:\\Users\\siirias\\Documents\\Aranda2022\\WEATHERSTATION\\converted\\weatherdata_202204021820_202204091628.csv" 
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
#highlight = "SBD1"
highlight = None
max_labels = 20
add_times_to_map = True
#start_ind = 0
#end_ind = -1
# start_ind = 296
# end_ind = 301
# filtered_indices = [317]
# plot_sets =[
#         ['snit_1',[289,290,301,302,313,314]],
#         ['snit_2',[288,291,300,303,312,315]],
#         ['snit_3',[287,292,299,304,311,316]],
#         ['snit_4',[286,293,298,305,310,318]],
#         ['snit_5',[285,294,297,306,309,319]],
#         ['snit_6',[284,295,296,307,308,320]],
#         ['aland_snit',260,278],
#         ['aland_1',[262,263,264,265,272,273,274,275,276,277,278]],
#         ['aland_2',265,269],
#         ['north_aland',279,282],
#         ['border_snit',283,289],
#         ['snit_a',290,295],
#         ['snit_b',296,301],
#         ['snit_c',302,307],
#         ['snit_d',308,313],
#         ['snit_e',314,320],
# #        ['snit_IU',343,350],
#         ['SR5',328,342],
#         ['hila',289,320]
#         ]
# map_shape = (5,10)

start_ind = 58
end_ind = 100
filtered_indices = []
map_shape = (5,10)
plot_sets = [
    ['cable1',58,100]
             ]
JustOne = 'cable1'
#JustOne = 'snit_Lagsk' #False
#JustOne = 'total' #False
#JustOne = 'RBRTEST' #False
#JustOne = 'SR5' #False
#JustOne = 'SR5_xtra' #False
#JustOne = 'hilasta_eespain' #False
#JustOne = 'hila' #False
#JustOne = 'snit_IU' #False

if(JustOne):
    if(JustOne == "snit_IU"):
        plot_sets = [['snit_IU',343,350]]
        map_area = None # None or list: [lat_min,lat_max,lon_min,lon_max]
        #Variable info: variable number, and min max values for plots, or None to both.
        variable_info = [[1,None,None],[4,None,None],\
                         [7,None,None],[8,None,None]]
    if(JustOne == "cable1"):
        plot_sets = [['cable1',58,100]]
        map_area = [18.0,27.0, 57,60.5]
        map_shape = (10,10)
        #Variable info: variable number, and min max values for plots, or None to both.
        variable_info = [[1,None,None],[4,None,None],\
                         [7,None,None],[8,None,None]]
    if(JustOne == "snit_Lagsk"):
        plot_sets = [['snit_lagsk',[262,351,352,353,354,455,356,357]]]
        map_area = None # None or list: [lat_min,lat_max,lon_min,lon_max]
        #Variable info: variable number, and min max values for plots, or None to both.
        variable_info = [[1,None,None],[4,None,None],\
                         [7,None,None],[8,None,None]]
    if(JustOne == "hila"):
        plot_sets = [['hilatmp',283,320]]
        map_area = [19.1,20.4,60.45,61.25]
        #Variable info: variable number, and min max values for plots, or None to both.
        variable_info = [[1,None,None],[4,None,None],\
                         [7,None,None],[8,None,None]]
        map_shape = (8,10)
        alpha_val = 0.75
    if(JustOne == "hilasta_eespain"):
        plot_sets = [['hilaeesp',283,-1]]
        map_area = [19.1,20.4,60.45,61.25]
        #Variable info: variable number, and min max values for plots, or None to both.
        variable_info = [[1,None,None],[4,None,None],\
                         [7,None,None],[8,None,None]]
        map_shape = (8,10)
        alpha_val = 0.75
    if(JustOne == "SR5"):
        plot_sets = [['SR5',328,342]]
        map_area = [18.5,21.0,59.7,61.4]
        #Variable info: variable number, and min max values for plots, or None to both.
        variable_info = [[1,None,None],[4,None,None],\
                         [7,None,None],[8,None,None]]
    if(JustOne == "SR5_xtra"):
        plot_sets = [['SR5_xtra',[303]+list(range(328,343))]]
        map_area = [18.5,21.0,59.7,61.4]
        #Variable info: variable number, and min max values for plots, or None to both.
        variable_info = [[1,None,None],[4,None,None],\
                         [7,None,None],[8,None,None]]
    if(JustOne == "total"):
        plot_sets = [['',0,-1]]
        map_area = None # None or list: [lat_min,lat_max,lon_min,lon_max]
        #Variable info: variable number, and min max values for plots, or None to both.
        variable_info = [[1,None,None],[4,None,None],\
                         [7,None,None],[8,None,None]]
    if(JustOne == "RBRTEST"):
        plot_sets = [['RBRTEST',0,-1]]
        map_area = None # None or list: [lat_min,lat_max,lon_min,lon_max]
        #Variable info: variable number, and min max values for plots, or None to both.
        variable_info = [[1,None,None],[5,None,None],\
                         [8,None,None]]
else:
    map_area = [18.5,21.0,59.7,61.4]
    #Variable info: variable number, and min max values for plots, or None to both.
    variable_info = [[1,3.0,13.0],[4,3.0,9.0],\
                     [7,4.0,7.0],[8,4.0,6.0]]


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

if weatherdata_file != "":
    weatherdata = pd.read_csv(weatherdata_file)
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
    in_files_tmp = [i for i in in_files_tmp if re.match(".*\da\.cnv", i)] # right types
    # then separate with index
    in_files = []
    for i in in_files_tmp:
        index_no = int(re.search(".*(\d\d\d\d)a\.cnv",i).groups()[0])
#        if( index_no >= start_ind and (end_ind<0 or index_no<=end_ind)):
        if( index_no in ok_index_list): #pick the ones listed
            if(index_no not in filtered_indices): #but not in black-listed ones
                in_files.append(i)
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
        lines = open(in_dir+in_file,'r').readlines()
        end_found = False  #search end to find start of data
        data = []
        columns = []
        long_names = []
        unit_names = []
        station_name = None
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
                    print("WARNING: station name failed:",l)
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
                    tmp_l= l                    
                    tmp_l = re.sub(",","",tmp_l) #fix extra comma in header
                    tmp_l = re.sub("(\d):(\d)",r"\1.\2",tmp_l) #fix : instead of . in time
                    the_time = re.search("\*\*.*:(.*)",tmp_l).groups()[0].strip()
                    the_time = dt.datetime.strptime(the_time,"%d.%m.%Y %H.%M")
                except:
                    print("WARNING, Can't parse time!: {}".format(l))
                    the_time = dt.datetime(2000,1,1)
                times.append(the_time)

            if(re.match("# start_time",l)):  
                try:
                    the_time = re.search(\
                             "# start_time = ([a-zA-z]* \d* \d* \d*:\d*:\d*)"\
                             ,l).groups()[0].strip()
                    #esim: Oct 15 2020 16:43:44
                    the_time = dt.datetime.strptime(the_time,"%b %d %Y %H:%M:%S")
                except:
                    print("WARNING, Can't parse time!: {}".format(l))
                    the_time = dt.datetime(2000,1,1)
                times.append(the_time)

            if(end_found):
                l_t = re.sub("\s\s*"," ",l.strip()).split(" ")
                l_t = list(map(lambda x: float(x),l_t))
                l_t.append(latitude)
                l_t.append(longitude)
                l_t.append(the_time)
                data.append(l_t)
            if(re.match('\*END\*',l)):
                end_found = True
        if(not station_name):
            station_name = "unknown"
            station_names.append(station_name)
            
        columns.append('Lat')
        columns.append('Lon')
        columns.append('Time')
        long_names.append('Latitude')
        long_names.append('Longitude')
        long_names.append('Time')
        ctd_data = pd.DataFrame(data,columns = columns)
        ctd_datas.append(ctd_data)


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
        plt.figure(figsize=(7,15))
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
        plt.ylabel("{} ({})".format(long_names[0], unit_names[0]))
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
        for [x_axis, x_label] in zip([time_list, lat_list, lon_list, dist_list],["Time","Latitude","Longitude","Distance (NM)"]):
            arranged_dat = sort_by_axis(profile_data,x_axis)
            sorted_x = np.sort(x_axis)
            if(x_label == "Time"):
                sorted_x = list(map(lambda x:x.to_datetime64(),sorted_x))
            fig = plt.figure(figsize=(15,7))
            plt.pcolormesh(sorted_x, depth_axis, arranged_dat, shading = 'auto', cmap = cmap)
            plt.gca().invert_yaxis()
            if(x_label == "Latitude"):
                plt.gca().invert_xaxis()
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
            plt.ylabel("{} ({})".format(long_names[0], unit_names[0]))
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
    if(weatherdata_file != ""):
        plt.plot(weatherdata['lon'],weatherdata['lat'],'k--', alpha = 0.2, transform = ccrs.PlateCarree())
#    plt.plot(lon_list,lat_list,'b-',transform = ccrs.PlateCarree())
    for [n,t,lat,lon] in zip(station_names,times, lat_list,lon_list):
        if(map_area is not None and \
               lon>map_area[0] and\
               lon<map_area[1] and\
               lat>map_area[2] and\
               lat<map_area[3]):
            text = n
            tsize = 10.0
            if add_times_to_map:
                text = "{}({})".format(text, t.strftime("%m.%d. %H"))
                tsize = 5.0
            plt.text(lon,lat,text,transform = ccrs.PlateCarree(),\
                     alpha=0.5, size = tsize, rotation = 30.0)
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
