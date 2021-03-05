# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 14:10:15 2021

@author: siirias
"""
text_field_template = \
"""
var marker =  new L.Marker([{}, {}], {{
    icon: new L.DivIcon({{
        className: 'my-div-icon',
        html: '<bold>{}</bold>'
    }})
}});
marker.bindTooltip("{}<br> {},{} <br> visits: {} ");
marker.addTo(stationNames)
"""


d = open("stations10.csv").readlines()
new_lines = []
for l in d:
    try:
        l = l.strip().split('\t')
        name = l[0]
        lat = float(l[1])
        lon = float(l[2])
        weight = float(l[3])
        size = min(weight*10.0,4000)
        new_lines.append(\
        'L.circle([{},{}], {}, {{color: "red",fillColor: "red",fillOpacity: 0.5}}).addTo(stationPoints).bindTooltip("{}<br> {},{} <br> visits: {} ");\n'\
            .format(lat,lon,size,name,lat,lon, weight)
            
        )
        new_lines.append(text_field_template.format(lat+1.2*size/(1800.0*60.0),lon,name+'<br>',\
                                                    name,lat,lon, weight))
    except ValueError:
        pass
    
template = open("template.html").readlines()
new_file = []
for l in template:
    if("//REPLACE WITH POINTS//" in l):
        for i in new_lines:
            new_file.append(i)
    else:
        new_file.append(l)
open("D:\\Data\\ArandaDataa\\measuring_points.html",'w').writelines(new_file)