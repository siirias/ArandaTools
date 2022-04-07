# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 22:02:34 2022

@author: siirias
"""
import datetime as dt
import numpy as np
import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# in_dir = "C:\\Users\\siirias\\Documents\\Aranda2022\\WEATHERSTATION\\nmea-message-2022-04-05\\"
in_dir = "C:\\Users\\siirias\\Documents\\Aranda2022\\WEATHERSTATION\\cable1\\"
in_file = "nmea-message-2022-04-05_01.25.21.log"

do_plots = False

out_dir = "C:\\Users\\siirias\\Documents\\Aranda2022\\WEATHERSTATION\\converted\\"
def log2csv(in_file):
    data = open(in_file,'r', encoding='ansi').readlines()
    variables = {}
    for line in data:
        try:
            var = re.search('\$([^,]+)',line).groups()[0]
            if(var not in variables):
                variables[var] = []
            variables[var].append(line)
        except AttributeError:
            print(line,'discarded')
    variables = {key:variables[key] for key in ['IIGLL', 'IIYDT', 'VAT3C','VAT4C','VACNS','VASAL','VAST1','VAST2','VAG11','VAPHP','VAT1C']}
    value_no = np.min(list(map(lambda x:len(variables[x]),variables)))
    data = []
    for i in range(value_no):
        d = {}
        d['time'] = dt.datetime.strptime(variables['IIYDT'][i],\
                                         '$IIYDT,%Y,%m,%d,%H%M%S,\n')
        tmp = re.search('\$IIGLL,\s*([\d]+)(\d\d\.[\d]+),(.),\s*([\d]+)(\d\d\.[\d]+),(.),',\
                  variables['IIGLL'][i]).groups()
        d['lat'] = float(tmp[0]) + float(tmp[1])/60.0
        if tmp[3]=='S':
            d['lat'] *= -1.0
        d['lon'] = float(tmp[3]) + float(tmp[4])/60.0
        if tmp[3]=='W':
            d['lon'] *= -1.0
        
        try:
            d['wind_spd'] = float(\
                                  re.search('\$VAST1,ST1 M/S 10M\s+([\d\.]+)',\
                                            variables['VAST1'][i]).groups()[0])
        except AttributeError:
            d['wind_spd'] = None
                                         
        try:
            d['wind_spd10min'] = float(\
                                  re.search('\$VAST1,ST1 M/S 10M\s+([\d\.]+)\s+([\d\.]+)',\
                                            variables['VAST1'][i]).groups()[1])
        except AttributeError:
            d['wind_spd10min'] = None

        d['wind_dir'] = float(\
                              re.search('\$VAG11,G11 DEG 01M\s+([-\d\.]+)',\
                                        variables['VAG11'][i]).groups()[0])

        d['air_pres'] = float(\
                              re.search('\$VAPHP,P   HPA 01H\s+([\d\.]+)',\
                                        variables['VAPHP'][i]).groups()[0])
        try:
            d['air_temp'] = float(\
                                  re.search('\$VAT1C,T1  C   01H\s+([-\d\.]+)',\
                                            variables['VAT1C'][i]).groups()[0])
        except AttributeError:
            d['air_temp'] = None
        try:
            d['salinity'] = float(\
                                  re.search('\$VASAL,SAL PSU 01H\s+([-\d\.]+)',\
                                            variables['VASAL'][i]).groups()[0])
        except AttributeError:
            d['salinity'] = None
        try:
            d['conductivity'] = float(\
                                  re.search('\$VACNS,CN  MMH 01H\s+([-\d\.]+)',\
                                            variables['VACNS'][i]).groups()[0])
        except AttributeError:
            d['conductivity'] = None
        try:
            d['sea_temperature'] = float(\
                                  re.search('\$VAT4C,T4  C   01H\s+([-\d\.]+)',\
                                            variables['VAT4C'][i]).groups()[0])
        except AttributeError:
            d['sea_temperature'] = None

        data.append(d)
    data = pd.DataFrame(data)
    return data

def angle2uv(angles, strengths):
    angles = np.array(angles)
    strengths = np.array(strengths)
    du = np.sin(2.0*np.pi*angles/360.0)
    dv = np.cos(2.0*np.pi*angles/360.0)
    du = du*strengths
    dv = dv*strengths
    return (du,dv)

in_files=[i for i in os.listdir(in_dir) if i.endswith('.log')]
weatherdata = pd.DataFrame()  
for in_file in in_files:
    d = log2csv(in_dir + in_file)
    # print(len(weatherdata),len(d))
    if  weatherdata.empty:
        weatherdata = d
    else:
        weatherdata = pd.concat([weatherdata, d])
weatherdata = weatherdata.sort_values('time')

out_name = 'weatherdata_{}_{}.csv'.format(\
                        weatherdata['time'].min().strftime('%Y%m%d%H%M'),\
                        weatherdata['time'].max().strftime('%Y%m%d%H%M')                                          )
weatherdata.to_csv(out_dir+out_name)
print('Saved: '+out_dir + out_name)

if do_plots:
    plt.figure(figsize = (10,10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines(resolution = '10m')
    plt.plot(weatherdata['lon'],weatherdata['lat'],'-.k',transform = ccrs.PlateCarree())

    plt.figure()
    plt.plot(weatherdata['time'],weatherdata['wind_spd'],'.r',alpha=0.1)
    plt.plot(weatherdata['time'],weatherdata['wind_spd10min'],'.b',alpha=0.1)
    dudv = angle2uv(weatherdata['wind_dir'], weatherdata['wind_spd'])
    step=100
    plt.quiver(weatherdata['time'][::step],0.0*weatherdata['wind_spd10min'][::step], dudv[0][::step], dudv[1][::step], scale = 500.0, alpha = 0.1, color = 'g')


