# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 11:23:01 2022

Creates ARALAB style index list,
the data needs to be in memory. show_ctd.py creates suitable data.

Used if needs the RALAB style file, but for one reason or not,
it is not available.
Depths need to be get from header files of the data or other such place.
@author: siirias
"""
ara_lats = list(map(lambda x: np.floor(x) + (x-np.floor(x))*0.6, lats))
ara_lons = list(map(lambda x: np.floor(x) + (x-np.floor(x))*0.6, lons))

a = list(map(lambda x: "01 {:04} {:10} N{:02.04f} E{:08.04f} xxx.00 {:}"\
             .format(x[0],x[1],x[2],x[3],x[4].strftime("%Y%m%d %H%M")),\
                 zip(station_indices, station_names, ara_lats, ara_lons, times[1::2])))
    
for i in a: print(i)