# -*- coding: utf-8 -*-
# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
'''
Tämä tekee Arandan matkasuunnitelman mcx-tiedostosta Leaflet-kartan (html-tiedoston)

Pohjana käytetään MyCruise_Leaflet_Routemap_template_variable_size.html-tiedostoa,
josta tehdään kopio, johon laitetaan matkaa koskevat tiedot oikeille paikoilleen.

Tämän kanssa samassa hakemistossa tulee olla seuraavat tiedostot:
- mcxFile.py
'''

import mcxFile as mcx
import os

#if(len(sys.argv)>1):
#    f_name=sys.argv[1]
#else:
#    f_name = input('Anna matka: ')
#from mcxFile import *



# %%
#f_name = input('Anna matka: ')
#f_name = "C:\\Users\\siirias\\Documents\\Aranda2020\\VRT_2020_syksy_current.mkx"
#f_name = "C:\\Users\\siirias\\Documents\\Aranda2020\\VRT_2020_syksy_extrasyvanne_pitka.mkx"
input_dir = "C:\\Users\\siirias\\Documents\\Aranda2021\\Ehdotukset\\"
files_to_handle = [i for i in os.listdir(input_dir) if i.endswith('.mkx')]

for f in files_to_handle:
    f_name = input_dir + f
    if '.MKX' in f_name.upper():
        acruise = mcx.MKXfile(f_name)
    else:
        acruise = mcx.MCXfile(f_name)
    olist = acruise.leaflethtml()






