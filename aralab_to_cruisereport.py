# -*- coding: utf-8 -*-
"""
Created on Fri May 21 08:39:58 2021

@author: siirias
"""
import re
import datetime as dt
import numpy as np
in_dir = "D:\\Data\\EuroArgoCruise\\"
out_dir = "D:\\Data\\EuroArgoCruise\\"
in_file = "ARAINDEX.DAT"
out_file = "report{}.txt".format(dt.datetime.now().strftime("%d%m%Y"))
out_file2 = "report:ist_UTC{}.txt".format(dt.datetime.now().strftime("%d%m%Y"))

first_index = 101
lines = open(in_dir+in_file).readlines()
out_file = open(out_dir+out_file,'w')
for l in lines:
    data = l.split()
    if( int(data[1])>=first_index):
        print(data)
        the_index = int(data[1])
        point_name = data[2]
        lat = re.search("(\d+)\.(\d+)",data[3]).groups()
        lat = float(lat[0])+(float('0.'+lat[1])*100.0/60.0)
        lon = re.search("(\d+)\.(\d+)",data[4]).groups()
        lon = float(lon[0])+(float('0.'+lon[1])*100.0/60.0)
        depth = float(data[5])
        start_time = dt.datetime.strptime(data[6]+data[7], "%Y%m%d%H%M") +\
                        dt.timedelta(hours=0)
        out_file.write("Indeksi {:04}, {} {:.0f}° {:0.3f}' N, {:.0f}° {:0.3f}' E, klo {}, syvyys {} m\n".format(
                the_index,
                point_name,
                np.floor(lat), (lat-np.floor(lat))*60.0,
                np.floor(lon), (lon-np.floor(lon))*60.0,
                start_time.strftime("%H.%M"),
                np.round(depth)
                ))
out_file.close()
