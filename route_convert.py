# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 16:26:39 2020

Converts MyCruise ascii file 
(File -> export cruise -> save route as latlon -> dd.dddd decimal degrees )
INto format that should be able to be read by Aranda command center
@author: siirias
"""
import re
import datetime as dt
#in_dir = "C:\\Users\\siirias\\Documents\\Aranda2020\\ValmiitEhdotukset\\"
#out_dir = "D:\\Data\\ArandaDataa\\navigointiesimerkki\\"
in_dir = 'C:\\Users\\siirias\\Documents\\Aranda2021\\CRuisePlan\\Plan\\'
out_dir = 'C:\\Users\\siirias\\Documents\\Aranda2021\\CRuisePlan\\Plan\\'
in_file = "EuroArgoCruise_v1.0.txt"

#in_file = "kokeilu_toteutunut_matka.txt"
out_file = re.sub("\..*",".csv",in_file)
trip_name = "FROM MyCruise"
trip_length = 24*9.5 # hours
start_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
end_time = (dt.datetime.now()+dt.timedelta(hours=trip_length)).strftime("%Y-%m-%d %H:%M:%S")

lines = open(in_dir+in_file,'r').readlines()
f = open(out_dir+out_file,'w')
f.write("{},,{},{}\n".format(trip_name, start_time, end_time))
for i in lines:
    print(i)
    line_dat = re.search("([\d\.]+) +([\d.]+) +(\d+) +(.*)",i).groups()
    lat = line_dat[0]
    lon = line_dat[1]
    name = line_dat[3]
    if( name == "P"):
        name = ""  # NyCruise waypoint 
    print("{},{},{},\n".format(name,lat,lon))
    f.write("{},{},{},\n".format(name,lat,lon))
f.close()