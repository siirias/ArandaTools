# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 15:14:19 2022

Compares one profile from Aranda
to another from Argo float

Very unfinished.

@author: siirias
"""
import matplotlib as mp
import matplotlib.pyplot as plt
import arandapy as apy
import xarray as xr
import matplotlib as mpl
import argohelper as ah  #This link between the two toolboxes should really be dealt with

indir_aranda = 'C:/Data/EuroArgoCruise/sbetulos/'
infile_aranda = 'a210110a.cnv'
indir_argo = 'C:/Data/ArgoData/ArgosForPlot/RBR_BalticProper/'
infile_argo = 'GL_PR_PF_6903706.nc'
outdir = 'C:/Data/ArgoData/Figures/'
fig_dpi = 300

profile_types = 3
argo_profile_no = 0
argo_prof_CTD = argo_profile_no*profile_types
argo_prof_O2 = argo_profile_no*profile_types + 2

ara_vars = ['t090C','sal00','sbeox0ML/L']
arg_vars = ['TEMP','PSAL','DOX2']
units = ['°C', 'PSU', 'ml/l']
titles = ['Temperature', 'Salinity', 'Oxygen']

aranda_profile = apy.read_aranda_file(indir_aranda + infile_aranda)
argo_profile = xr.open_dataset(indir_argo + infile_argo)
fig = plt.figure(figsize = (10,5))
subplot_no =101 + 10*len(ara_vars)
for ara_var,arg_var,unit,title in zip(ara_vars, arg_vars, units, titles):
    aranda_p_var = aranda_profile[0][ara_var]
    aranda_p_dep = aranda_profile[0]['prDM']
    a_p = argo_prof_CTD
    if(arg_var in ['DOX2']):
        a_p = argo_prof_O2
    argo_p_var = argo_profile[arg_var][a_p].copy()
    argo_p_dep =  argo_profile['PRES'][a_p].copy()
    arg_lat = float(argo_profile['LATITUDE'][a_p])
    arg_lon = float(argo_profile['LONGITUDE'][a_p])
    if(arg_var in ['DOX2']): #conversion umol/kg -> ml/l
        T = ah.interpolate_data_to_depths(argo_profile['TEMP'][argo_prof_CTD],
                                          argo_profile['PRES'][argo_prof_CTD],
                                          argo_profile['PRES'][argo_prof_O2])[0]
        S = ah.interpolate_data_to_depths(argo_profile['PSAL'][argo_prof_CTD],
                                          argo_profile['PRES'][argo_prof_CTD],
                                          argo_profile['PRES'][argo_prof_O2])[0]
        argo_p_var = ah.o2_umolkg_to_mll(argo_p_var,
                            T,
                            S,
                            arg_lon, arg_lat, argo_p_dep)

    ax = plt.subplot(subplot_no)
    plt.plot(aranda_p_var, aranda_p_dep,label='ship')
    plt.plot(argo_p_var, argo_p_dep, label = 'Argo')
    
    plt.legend()
    ax.invert_yaxis()
    ax.title.set_text(title)
    ax.set_ylabel('Pressure (db)')
    ax.set_xlabel(unit)
    subplot_no += 1
fig.tight_layout()
outfilename = 'deployment_profiles.png'
plt.savefig(outdir + outfilename, dpi = fig_dpi, bbox_inches='tight')