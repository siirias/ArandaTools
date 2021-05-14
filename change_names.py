# -*- coding: utf-8 -*-
"""
Created on Thu May  6 19:01:08 2021
Script to replace old, rather cryptic, names of  certain grid with
something more readable.
@author: siirias
"""
import re

point_pairs = {
#       '':'SMG20_A1',
       'JATKO20_1':'SMG20_A2',
       'YLA20_01':'SMG20_A3',
       'YLA20_02':'SMG20_A4',
       'YLA20_03':'SMG20_A5',
       'YLA20_03B':'SMG20_A6',
       'UI2020A':'SMG20_A7',
#       '':'SMG20_B1',
       'JATKO20_2':'SMG20_B2',
       'HILA20_5':'SMG20_B3',
       'HILA20_4':'SMG20_B4',
       'HILA20_3':'SMG20_B5',
       'HILA20_2':'SMG20_B6',
       'HILA20_1':'SMG20_B7',
#        '':'SMG20_C1',
       'JATKO20_3':'SMG20_C2',
       'HILA20_6':'SMG20_C3',
       'HILA20_7':'SMG20_C4',
       'HILA20_8':'SMG20_C5',
       'HILA20_9':'SMG20_C6',
       'HILA20_10':'SMG20_C7',
#        '':'SMG20_D1',
       'JATKO20_4':'SMG20_D2',
       'KUOP20_05':'SMG20_D3',
       'UI2020KUOPPA':'SMG20_D4',
       'KUOP20_03':'SMG20_D5',
#        '':'SMG20_D6', # SR5
       'KUOP20_01':'SMG20_D7',
       'Kuop20_01':'SMG20_D7',
#        '':'SMG20_E1',
       'JATKO20_5':'SMG20_E2',
       'YLAB20_01':'SMG20_E3',
       'XTRH20_6':'SMG20_E4',
       'XTRH20_1':'SMG20_E5',
       'ALA20_05':'SMG20_E6',
       'UI2020FB':'SMG20_E7',
#        '':'SMG20_F1',
       'JATKO20_6':'SMG20_F2',
       'JATKO20_7':'SMG20_F3',
       'JATKO20_8':'SMG20_F4',
       'JATKO20_9':'SMG20_F5',
       'JATKO20_10':'SMG20_F6',
       'UI2020F':'SMG20_F7',
#        '':'SMG20_G1',
#        '':'SMG20_G2',
#        '':'SMG20_G3',
#        '':'SMG20_G4',
#        '':'SMG20_G5',
#        '':'SMG20_G6',
#        '':'SMG20_G7',
#        '':'SMG20_H1',
#        '':'SMG20_H2',
#        '':'SMG20_H3',
#        '':'SMG20_H4',
#        '':'SMG20_H5',
#        '':'SMG20_H6',
#        '':'SMG20_H7',
#        '':'SMG20_I1',
#        '':'SMG20_I2',
#        '':'SMG20_I3',
#        '':'SMG20_I4',
#        '':'SMG20_I5',
#        '':'SMG20_I6',
#        '':'SMG20_I7',
       }


in_dir = 'C:\\Users\\siirias\\Documents\\Aranda2021\Ehdotukset\\'
in_file = "koko_matka_v0_5_reverse.mkx"
out_file = "koko_matka_v0_5_new_names.mkx"

old_name = "SMG20_"
new_name = "SEME_"
lines = open(in_dir+in_file).readlines()
new_lines = []
for line in lines:
    new_line = line
    for i in point_pairs:
        if(i in new_line):
            new_line = re.sub("<name>{}</name>".format(i),
                              "<name>{}</name>".format(point_pairs[i]),new_line)
    new_line = re.sub(old_name,new_name,new_line)
    new_lines.append(new_line)
        
open(in_dir+out_file,'w').writelines(new_lines)
