# -*- coding: utf-8 -*-
"""
Created on Fri May 14 12:04:00 2021

Unfinished, target is to make a simple gui for converting all kind
of various coordinate formats with minimum interactions.
@author: siirias
"""

import tkinter as tk
import re
import numpy as np


# class MyCalc(tk.Frame):
#     def __init__(self, master = None):
#         tk.Frame.__init__(self,master)
#         self.pack(fill=tk.BOTH,expand=1)
#         text = tk.Text(window, height = 1, width = 20)
#         #text.insert(tk.INSERT, "Hello.....")
#         #text.insert(tk.END, "Bye Bye.....")
#         text.pack()
#         calc_button = tk.Button(text ="calculate", command = self.calculate_coords)
#         calc_button.place(x=0,y=100)

#     def calculate_coords(self):
#         exit()


# window = tk.Tk()
# app = MyCalc(window)
# window.wm_title("Coord_converter")
# window.geometry("800x300")
# window.mainloop()

print("Input coords")
coords = input()
#coords = "57.447N 20.056E"
#coords = "57.447N"
format_found = False
tmp_dat = re.search("(\d+\.\d+\s*)([NS]?)[,_]*\s*(\d+\.\d+\s*)([EW]?)",coords)
if(tmp_dat): #this was found
    format_found = True
    print("Type, two coords, degree decimal")
    tmp_lat = float(tmp_dat.groups()[0])
    tmp_lon = float(tmp_dat.groups()[2])
    print(coords)
    print("{:.0f}° {:.3f}' {}  {:.0f}° {:.3f}' {}".format(\
          np.floor(tmp_lat),
          (tmp_lat-np.floor(tmp_lat))*60.0,tmp_dat.groups()[1],
          np.floor(tmp_lon),
          (tmp_lon-np.floor(tmp_lon))*60.0,tmp_dat.groups()[3]
            ))
if(not format_found):
    tmp_dat = re.search("(\d+\.\d+\s*)([NSEW])",coords)
    if(tmp_dat): #this was found
        format_found = True
        print("Type, one coord, degree decimal")
        tmp = float(tmp_dat.groups()[0])
        print(coords)
        print("{:.0f}° {:.3f}' {}".format(\
              np.floor(tmp),
              (tmp-np.floor(tmp))*60.0,tmp_dat.groups()[1]
                ))
if(not format_found):
    tmp_dat = re.search("[Ll]at[^\d]*(\d+\.\d+\s*)[^\d]*[lL]on[^\d]*(\d+\.\d+)",coords)
    if(tmp_dat): #this was found
        format_found = True
        print("Type, one coord, degree decimal")
        tmp_lat = float(tmp_dat.groups()[0])
        tmp_lon = float(tmp_dat.groups()[1])
        print(coords)
        print("{:.0f}° {:.3f}' N {:.0f}° {:.3f}' E".format(\
              np.floor(tmp_lat),
              (tmp_lat-np.floor(tmp_lat))*60.0,
              np.floor(tmp_lon),
              (tmp_lon-np.floor(tmp_lon))*60.0
                ))
if(not format_found):
    print("unknown format")