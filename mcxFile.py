# MCX-file unit

from pathlib import Path
import strutils_pa as strpa
import math
from datetime import datetime
import re
import xml.etree.ElementTree as ET

def mon2num(mon):
#================
# changes three (or more) letter month name mon to it's two digit presentation 01...12
    m = mon.upper()[0:3]
    mons = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
    for i in range(len(mons)):
        if m == mons[i]:
            id = i+1
    return str(id).rjust(2,'0')

def child_node_text(node,what):
#==============================
    child = node.find(what)
    if child != None:
        r = child.text
    else:
        r = ''
    return r

#==============================
mcx_html_tmpl = [
    '<!DOCTYPE html>',
    '<html>',
    '  <head>',
    '    <title>OTSIKKO</title>',
    '    <meta charset="utf-8" />',
    '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
    '    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.5.1/dist/leaflet.css" integrity="sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ==" crossorigin=""/>',
    '',
    '    <style>',
    '      html,body {',
    '        width: 100%;',
    '        height: 100%;',
    '        margin: 2%;',
    '        padding: 0;',
    '      }',
    '      #map {',
    '        position: absolute;',
    '        bottom: 2%;',
    '        top: 2%;',
    '        width: 90%;',
    '        height: 95%;',
    '        }',
    '      .info { padding: 6px 8px; font: 14px/16px Arial, Helvetica, sans-serif; background: white; background: rgba(255,255,255,0.8); box-shadow: 0 0 15px rgba(0,0,0,0.2); border-radius: 5px; } .info h4 { margin: 0 0 5px; color: #777; }',
    '      .legend { text-align: left; line-height: 18px; color: #555; } .legend i { width: 18px; height: 18px; float: left; margin-right: 8px; opacity: 0.7; }',
    '    </style>',
    '  </head>',
    '  <body>',
    '      <div id="map"></div>',
    '      <script src="https://unpkg.com/leaflet@1.5.1/dist/leaflet.js" integrity="sha512-GffPMF3RvMeYyc1LWMHtK8EbPv0iNZ8/oTtHPx9/cc2ILxQ+u905qIwdpULaqDkyBKgOaB57QTMg7ztg8Jm2Og==" crossorigin=""></script>',
    '      <script src="https://unpkg.com/leaflet" type="text/javascript"></script>',
    '      <script src="https://unpkg.com/leaflet-ant-path" type="text/javascript"></script>',
    '      <link rel="stylesheet" href="https://ppete2.github.io/Leaflet.PolylineMeasure/Leaflet.PolylineMeasure.css"/>',
    '      <script src="https://ppete2.github.io/Leaflet.PolylineMeasure/Leaflet.PolylineMeasure.js"></script>',
    '    <script>',
    '',
    '//pisteet ja reitti',
    '',
    '//    GRID LINES',
    '      var latlongrid = L.layerGroup();',
    '      latlongrid.onAdd = function(map) {',
    '        for (var i = 50; i < 71; i++) {L.polyline([[i*1.0, -180.0],[i*1.0, 180.0]], {color: \'black\', weight: 1, opacity: 0.2}).addTo(this);}',
    '        for (var i = 0; i < 61; i++) {L.polyline([[0.0, i*1.0],[80.0, i*1.0],], {color: \'black\', weight: 1, opacity: 0.2}).addTo(this);}',
    '      }',
    '',
    '      function style(feature) {',
    '        return {',
    '          weight: 2,',
    '          opacity: 1,',
    '          color: \'white\',',
    '          dashArray: \'3\',',
    '          fillOpacity: 0.7,',
    '          fillColor: getColor(feature.properties.visits)',
    '        };',
    '      }',
    '',
    '      function highlightFeature(e) {',
    '        var layer = e.target;',
    '        layer.setStyle({',
    '          weight: 5,',
    '          color: \'#666\',',
    '          dashArray: \'\',',
    '          fillOpacity: 0.7',
    '        });',
    '        if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {layer.bringToFront();}',
    '        info.update(layer.feature.properties);',
    '      }',
    '',
    '      var geojson;',
    '',
    '      function resetHighlight(e) {',
    '        geojson.resetStyle(e.target);',
    '        info.update();',
    '      }',
    '',
    '      function zoomToFeature(e) {',
    '        map.fitBounds(e.target.getBounds());',
    '      }',
    '',
    '      function onEachFeature(feature, layer) {',
    '        layer.on({',
    '          mouseover: highlightFeature,',
    '          mouseout: resetHighlight,',
    '          click: zoomToFeature',
    '        });',
    '      }',
    '',
    '//    INFO',
    '      var info = L.control();',
    '',
    '      info.onAdd = function (map) {',
    '        this._div = L.DomUtil.create(\'div\', \'info\');',
    '        this.update();',
    '        return this._div;',
    '      };',
    '',
    '      info.update = function (props) {',
    '        this._div.innerHTML = \'<h4 style="color: #0000CC;">Cruise route of</h4> <br> - \';',
    '      };',
    '',
    '//    LEGEND',
    '      var legend = L.control({position: \'bottomright\'});',
    '',
    '      legend.onAdd = function (map) {',
    '        var div = L.DomUtil.create(\'div\', \'info legend\'),',
    '            clrRed = \'red\',',
    '            clrGreen = \'green\';',
    '        div.innerHTML = \'<h4 style="color: #0000CC;">Color of stations</h4>\'+',
    '          \'<i style="background: \'+clrGreen+\'"></i> in Finnish EEZ<br>\'+',
    '          \'<i style="background: \'+clrRed+\'"></i> \' + \'outside of Finnish EEZ\';',
    '        return div;',
    '      };',
    '',
    '//    CURSOR POSITION',
    '      var cursorinfo = L.control({position: \'bottomleft\'});',
    '',
    '      cursorinfo.onAdd = function (map) {',
    '        this._div = L.DomUtil.create(\'div\', \'info info2\');',
    '        this.update();',
    '        return this._div;',
    '      };',
    '',
    '      cursorinfo.update = function (props) {',
    '        this._div.innerHTML = \'Cursor position<br/>\';',
    '      };',
    '',
    '//    MAP',
    '      var map = L.map(\'map\', {center:[60.517167, 21.280833], zoom: 5});',
    '      mapLink = \'<a href="http://openstreetmap.org">OpenStreetMap</a>\';',
    '',
    '      var strmaplayer = L.tileLayer(',
    '        \'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png\', {',
    '        attribution: \'&copy; \' + mapLink + \' Contributors\',',
    '        maxZoom: 20,',
    '      }).addTo(map);',
    '',
    '      var positron = L.tileLayer(\'http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png\', {',
    '        attribution: \'�OpenStreetMap, �CartoDB\',',
    '      });',
    '',
    '      var Esri_OceanBasemap = L.tileLayer(\'http://server.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}\', {',
    '        attribution: \'Tiles &copy; Esri &mdash; Sources: GEBCO, NOAA, CHS, OSU, UNH, CSUMB, National Geographic, DeLorme, NAVTEQ, and Esri\',',
    '        maxZoom: 20',
    '      });',
    '',
    '      var Esri_WorldTopoMap = L.tileLayer(\'http://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}\', {',
    '        attribution: \'Sources: Esri, HERE, Garmin, Intermap, increment P Corp., GEBCO, USGS, FAO, NPS, NRCAN, GeoBase, IGN, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), (c) OpenStreetMap contributors, and the GIS User Community\',',
    '        maxZoom: 20',
    '      });',
    '',
    '      var Esri_WorldStreetMap = L.tileLayer(\'http://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}\', {',
    '        attribution: \'Sources: Esri, HERE, Garmin, USGS, Intermap, INCREMENT P, NRCan, Esri Japan, METI, Esri China (Hong Kong), Esri Korea, Esri (Thailand), NGCC, (c) OpenStreetMap contributors, and the GIS User Community\',',
    '        maxZoom: 20',
    '      });',
    '',
    '      var opentopo = L.tileLayer(\'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png\', {',
    '        attribution: \'�OpenStreetMap, �CartoDB\',',
    '      });',
    '',
    '      var bathymetryLayer = L.tileLayer.wms("http://ows.emodnet-bathymetry.eu/wms", {',
    '        layers: \'emodnet:mean_atlas_land\',',
    '        format: \'image/png\',',
    '        transparent: true,',
    '        attribution: "Emodnet bathymetry",',
    '        opacity: 0.8',
    '      });',
    '',
    '      var coastlinesLayer = L.tileLayer.wms("http://ows.emodnet-bathymetry.eu/wms", {',
    '        layers: \'coastlines\',',
    '        format: \'image/png\',',
    '        transparent: true,',
    '        attribution: "Emodnet bathymetry",',
    '        opacity: 0.8',
    '      });',
    '',
    '      var bathymetryGroupLayer = L.layerGroup([bathymetryLayer, coastlinesLayer]);',
    '',
    '      var contourLayer = L.tileLayer.wms("http://ows.emodnet-bathymetry.eu/wms", {',
    '        layers: \'emodnet:contours\',',
    '        format: \'image/png\',',
    '        transparent: true,',
    '        attribution: "Emodnet bathymetry",',
    '        opacity: 0.8',
    '      });',
    '',
    '      var depthcontours = L.layerGroup([contourLayer]);',
    '',
    '      L.Control.MousePosition = L.Control.extend({',
    '        options: {',
    '          position: \'bottomleft\',',
    '          separator: \'<br>\',',
    '          emptyString: \'Cursor coordinates<br>0&deg;N<br>0&deg;E\',',
    '          lngFirst: false,',
    '          numDigits: 5,',
    '          lngFormatter: function(num) {',
    '            var direction = (num < 0) ? \'W\' : \'E\';',
    '            var degzero = (num < 10) ? \'0\' : \'\';',
    '            var minzero = ((Math.abs(num)-Math.abs(Math.trunc(num)))*60 < 10) ? \'0\' : \'\';',
    '            var formatted = degzero + Math.abs(L.Util.formatNum(num, 5)) + \'&deg; \' + direction + \' = \' + degzero + Math.abs(Math.trunc(num)) + \'&deg; \' + minzero + L.Util.formatNum((Math.abs(num)-Math.abs(Math.trunc(num)))*60,2) + \'&lsquo; \' + direction;',
    '            return formatted;',
    '          },',
    '          latFormatter: function(num) {',
    '            var direction = (num < 0) ? \'S\' : \'N\';',
    '            var degzero = (num < 10) ? \'0\' : \'\';',
    '            var minzero = ((Math.abs(num)-Math.abs(Math.trunc(num)))*60 < 10) ? \'0\' : \'\';',
    '            var formatted = degzero + Math.abs(L.Util.formatNum(num, 5)) + \'&deg; \' + direction + \' = \' + degzero + Math.abs(Math.trunc(num)) + \'&deg; \' + minzero + L.Util.formatNum((Math.abs(num)-Math.abs(Math.trunc(num)))*60,2) + \'&lsquo; \' + direction;',
    '            return formatted;',
    '          },',
    '          prefix: \'<h4 style="color: #0000CC;">Cursor position</h4>\'',
    '        },',
    '',
    '        onAdd: function (map) {',
    '          this._container = L.DomUtil.create(\'div\', \'leaflet-control-mouseposition\');',
    '          L.DomEvent.disableClickPropagation(this._container);',
    '          map.on(\'mousemove\', this._onMouseMove, this);',
    '//          this._container.innerHTML=this.options.emptyString;',
    '          return this._container;',
    '        },',
    '',
    '        onRemove: function (map) {',
    '          map.off(\'mousemove\', this._onMouseMove)',
    '        },',
    '',
    '        _onMouseMove: function (e) {',
    '          var lng = this.options.lngFormatter ? this.options.lngFormatter(e.latlng.lng) : L.Util.formatNum(e.latlng.lng, this.options.numDigits);',
    '          var lat = this.options.latFormatter ? this.options.latFormatter(e.latlng.lat) : L.Util.formatNum(e.latlng.lat, this.options.numDigits);',
    '          var value = this.options.lngFirst ? lng + this.options.separator + lat : lat + this.options.separator + lng;',
    '          var prefixAndValue = this.options.prefix + value;',
    '//          this._container.innerHTML = prefixAndValue;',
    '          cursorinfo._div.innerHTML = prefixAndValue;',
    '',
    '        }',
    '      });',
    '',
    '      var fairways = new L.LayerGroup();',
    '      var fairWays =',
    '        L.tileLayer.wms(\'https://extranet.liikennevirasto.fi/inspirepalvelu/avoin/wms\', {',
    '          layers: \'vaylat,vaylaalueet\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          maxZoom: 18,',
    '          minZoom: 7,',
    '          attribution: \'CC 4.0 Liikennevirasto. Ei navigointikäyttöön. Ei täytä virallisen merikartan vaatimuksia.\',',
    '      }).addTo(fairways);',
    '',
    '      var eez = new L.LayerGroup();',
    '      var eeZ =',
    '        L.tileLayer.wms(\'http://geo.vliz.be/geoserver/MarineRegions/wms\', {',
    '          layers: \'eez_boundaries\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          attribution: \'Marineregions.org.\',',
    '      }).addTo(eez);',
    '',
    '      var internalwaters = new L.LayerGroup();',
    '      var internalWaters =',
    '        L.tileLayer.wms(\'http://geo.vliz.be/geoserver/MarineRegions/wms\', {',
    '          layers: \'eez_internal_waters\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          attribution: \'Marineregions.org.\',',
    '      }).addTo(internalwaters);',
    '',
    '      var internalwaters12 = new L.LayerGroup();',
    '      var internalWaters12 =',
    '        L.tileLayer.wms(\'http://geo.vliz.be/geoserver/MarineRegions/wms\', {',
    '          layers: \'eez_12nm\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          attribution: \'Marineregions.org.\',',
    '      }).addTo(internalwaters12);',
    '',
    '      var helcomareaboundaries = new L.LayerGroup();',
    '      var helcomAreaboundaries =',
    '        L.tileLayer.wms(\'https://maps.helcom.fi/arcgis/services/MADS/Sea_environmental_monitoring/MapServer/WmsServer\', {',
    '          layers: \'89\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          attribution: \'HELCOM.\',',
    '      }).addTo(helcomareaboundaries);',
    '',
    '      var helcomareas = new L.LayerGroup();',
    '      var helcomAreas =',
    '        L.tileLayer.wms(\'https://maps.helcom.fi/arcgis/services/MADS/Sea_environmental_monitoring/MapServer/WmsServer\', {',
    '          layers: \'88\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          attribution: \'HELCOM.\',',
    '      }).addTo(helcomareas);',
    '',
    '      var mNavAttr = \'--- Merikorttipalvelu perustuu Liikenneviraston tuottaman rasterimuotoiseen merikartta-aineistoon. Käyttölupa CC 4.0\'',
    '        +\' Lähde: Liikennevirasto. Ei navigointikäyttöön. Ei täytä virallisen merikartan vaatimuksia.\';',
    '',
    '      var navigate = new L.LayerGroup();',
    '      var Navigate     =',
    '        L.tileLayer.wms(\'https://julkinen.traficom.fi/s57/wms\', {',
    '          layers: \'cells\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          minZoom: 7,',
    '          attribution: mNavAttr',
    '      }).addTo(navigate);',
    '',
    '      var bshcwater = new L.LayerGroup();',
    '      var Bshcwater =',
    '        L.tileLayer.wms(\'http://data.bshc.pro/ogc/bsbd-0.0.4/wms\', {',
    '          layers: \'water\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          minZoom: 5,',
    '          attribution: \'BSHC\'',
    '      }).addTo(bshcwater);',
    '',
    '      var mllAttr =\' Maanmittauslaitoksen nimipalvelu\';',
    '      var nimet = new L.LayerGroup();',
    '      var Nimet =',
    '        L.tileLayer.wms(\'https://inspire-wms.maanmittauslaitos.fi/inspire-wms/GN/wms\', {',
    '          layers: \'GN.GeographicalNames\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          minzoom: 5,',
    '          attribution: mllAttr',
    '      }).addTo(nimet);',
    '',
    '      var openseamap = new L.LayerGroup();',
    '      var openSeaMap =',
    '        L.tileLayer(\'http://tiles.openseamap.org/seamark/{z}/{x}/{y}.png\', {minZoom: 6}).addTo(openseamap);',
    '',
    '      L.Map.mergeOptions({positionControl: false});',
    '',
    '      L.Map.addInitHook(function () {',
    '        if (this.options.positionControl) {',
    '          this.positionControl = new L.Control.MousePosition();',
    '          this.addControl(this.positionControl);',
    '        }',
    '      });',
    '',
    '      L.control.mousePosition = function (options) {return new L.Control.MousePosition(options);};',
    '      L.control.mousePosition().addTo(map);',
    '',
    '      L.control.scale ({maxWidth:240, metric:true, imperial:false, position: \'bottomleft\'}).addTo (map);',
    '      let polylineMeasure = L.control.polylineMeasure ({position:\'topleft\', unit:\'metres\', showBearings:true, clearMeasurementsOnStop: false, showClearControl: true, showUnitControl: true})',
    '      polylineMeasure.addTo (map);',

    '      function debugevent(e) { console.debug(e.type, e, polylineMeasure._currentLine) }',
    '      map.on(\'polylinemeasure:toggle\', debugevent);',
    '      map.on(\'polylinemeasure:start\', debugevent);',
    '      map.on(\'polylinemeasure:resume\', debugevent);',
    '      map.on(\'polylinemeasure:finish\', debugevent);',
    '      map.on(\'polylinemeasure:clear\', debugevent);',
    '      map.on(\'polylinemeasure:add\', debugevent);',
    '      map.on(\'polylinemeasure:insert\', debugevent);',
    '      map.on(\'polylinemeasure:move\', debugevent);',
    '      map.on(\'polylinemeasure:remove\', debugevent);',
    '',  
    '      info.addTo(map);',
    '      cursorinfo.addTo(map);',
    '      legend.addTo(map);',
    '',
    '//    Stations and route line are on the map by default, other layers not',
    '      stationPoints.addTo(map);',
    '      routeLine.addTo(map);',
    '',
    '      var baseMaps = {',
    '        "StreetMap"             : strmaplayer,',
    '        "Positron"              : positron,',
    '        "ESRI OceanBasemap"     : Esri_OceanBasemap,',
    '        "ESRI Worl_Topo_Map"    : Esri_WorldTopoMap,',
    '        "ESRI World_Street_Map" : Esri_WorldStreetMap,',
    '        "Topo"                  : opentopo}',
    '',
    '      var overlayMaps = {',
    '        "EMODnet Bathymetry"            : bathymetryGroupLayer,',
    '        "BSHC Baltic Sea Bathymetry"    : bshcwater,',
    '        "EMODnet depth contours"        : depthcontours,',
    '        "EEZ"                           : eez,',
    '        "Internal waters"               : internalwaters,',
    '        "Internal waters 12 nm"         : internalwaters12,',
    '        "HELCOM areas"                  : helcomareas,',
    '        "HELCOM area boundaries"        : helcomareaboundaries,',
    '        "Open seamap"                   : openseamap,',
    '        "Finnish fairways"              : fairways,',
    '        "Finnish navigation chart"      : navigate,',
    '        "Latitude-longitude grid"       : latlongrid,',
    '        "Stations of the cruise"        : stationPoints,',
    '        "Routeline of the cruise"       : routeLine,',
    '        "Animated route of the cruise"  : antLine,',
    '        "Finnish place names"           : nimet',
    '      }',
    '',
    '      L.control.layers(baseMaps, overlayMaps).addTo(map);',
    '',
    '    </script>',
    '  </body>',
    '</html>',
    '']

leaflet_map_template = [
    '<!DOCTYPE html>',
    '<html>',
    '  <head>',
    '    <title>OTSIKKO</title>',
    '    <meta charset="utf-8" />',
    '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
    '    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.5.1/dist/leaflet.css" integrity="sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ==" crossorigin=""/>',
    '',
    '    <style>',
    '      html,body {',
    '        width: 100%;',
    '        height: 100%;',
    '        margin: 2%;',
    '        padding: 0;',
    '      }',
    '      #map {',
    '        position: absolute;',
    '        bottom: 2%;',
    '        top: 2%;',
    '        width: 90%;',
    '        height: 95%;',
    '        }',
    '      .info { padding: 6px 8px; font: 14px/16px Arial, Helvetica, sans-serif; background: white; background: rgba(255,255,255,0.8); box-shadow: 0 0 15px rgba(0,0,0,0.2); border-radius: 5px; } .info h4 { margin: 0 0 5px; color: #777; }',
    '      .legend { text-align: left; line-height: 18px; color: #555; } .legend i { width: 18px; height: 18px; float: left; margin-right: 8px; opacity: 0.7; }',
    '    </style>',
    '  </head>',
    '  <body>',
    '      <div id="map"></div>',
    '      <script src="https://unpkg.com/leaflet@1.5.1/dist/leaflet.js" integrity="sha512-GffPMF3RvMeYyc1LWMHtK8EbPv0iNZ8/oTtHPx9/cc2ILxQ+u905qIwdpULaqDkyBKgOaB57QTMg7ztg8Jm2Og==" crossorigin=""></script>',
    '      <script src="https://unpkg.com/leaflet" type="text/javascript"></script>',
    '      <script src="https://unpkg.com/leaflet-ant-path" type="text/javascript"></script>',
    '    <script>',
    '',
    '      var stationPoints = L.layerGroup();',
    '',
    '//    CIRCLES SHALL BE PUT HERE',
    '',
    '      var routeLine = L.layerGroup();',
    '      var antLine   = L.layerGroup();',
    '',
    '//    ROUTE LINE SHALL BE PUT HERE',
    '      L.polyline(route, {color: \'blue\', weight: 1}).addTo(routeLine);',
    '',
    '      antroute = L.polyline.antPath(route, {',
    '          "delay": 1000,',
    '          "dashArray": [10,10],',
    '          "weight": 3,',
    '          "color": "#0000FF",',
    '          "pulseColor": "#FFFFFF",',
    '          "paused": false ,',
    '          "reverse": false ,',
    '          "hardwareAccelerated": true',
    '      }).addTo(antLine)',
    '',
    '//    GRID LINES',
    '      var latlongrid = L.layerGroup();',
    '      latlongrid.onAdd = function(map) {',
    '        for (var i = 50; i < 71; i++) {L.polyline([[i*1.0, -180.0],[i*1.0, 180.0]], {color: \'black\', weight: 1, opacity: 0.2}).addTo(this);}',
    '        for (var i = 0; i < 61; i++) {L.polyline([[0.0, i*1.0],[80.0, i*1.0],], {color: \'black\', weight: 1, opacity: 0.2}).addTo(this);}',
    '      }',
    '',
    '      function style(feature) {',
    '        return {',
    '          weight: 2,',
    '          opacity: 1,',
    '          color: \'white\',',
    '          dashArray: \'3\',',
    '          fillOpacity: 0.7,',
    '          fillColor: getColor(feature.properties.visits)',
    '        };',
    '      }',
    '',
    '      function highlightFeature(e) {',
    '        var layer = e.target;',
    '        layer.setStyle({',
    '          weight: 5,',
    '          color: \'#666\',',
    '          dashArray: \'\',',
    '          fillOpacity: 0.7',
    '        });',
    '        if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {layer.bringToFront();}',
    '        info.update(layer.feature.properties);',
    '      }',
    '',
    '      var geojson;',
    '',
    '      function resetHighlight(e) {',
    '        geojson.resetStyle(e.target);',
    '        info.update();',
    '      }',
    '',
    '      function zoomToFeature(e) {',
    '        map.fitBounds(e.target.getBounds());',
    '      }',
    '',
    '      function onEachFeature(feature, layer) {',
    '        layer.on({',
    '          mouseover: highlightFeature,',
    '          mouseout: resetHighlight,',
    '          click: zoomToFeature',
    '        });',
    '      }',
    '',
    '//    INFO',
    '      var info = L.control();',
    '',
    '      info.onAdd = function (map) {',
    '        this._div = L.DomUtil.create(\'div\', \'info\');',
    '        this.update();',
    '        return this._div;',
    '      };',
    '',
    '      info.update = function (props) {',
    '        this._div.innerHTML = \'<h4 style="color: #0000CC;">Cruise route of</h4>BothnianSea2017<br>2017-05-02 - 2017-05-13\';',
    '      };',
    '',
    '//    LEGEND',
    '      var legend = L.control({position: \'bottomright\'});',
    '',
    '      legend.onAdd = function (map) {',
    '        var div = L.DomUtil.create(\'div\', \'info legend\'),',
    '            clrRed = \'red\',',
    '            clrGreen = \'green\';',
    '        div.innerHTML = \'<h4 style="color: #0000CC;">Color of stations</h4>\'+',
    '          \'<i style="background: \'+clrGreen+\'"></i> in Finnish EEZ<br>\'+',
    '          \'<i style="background: \'+clrRed+\'"></i> \' + \'outside of Finnish EEZ\';',
    '        return div;',
    '      };',
    '',
    '//    CURSOR POSITION',
    '      var cursorinfo = L.control({position: \'bottomleft\'});',
    '',
    '      cursorinfo.onAdd = function (map) {',
    '        this._div = L.DomUtil.create(\'div\', \'info info2\');',
    '        this.update();',
    '        return this._div;',
    '      };',
    '',
    '      cursorinfo.update = function (props) {',
    '        this._div.innerHTML = \'Cursor position<br/>\';',
    '      };',
    '',
    '//    MAP',
    '      var map = L.map(\'map\', {center:[60.517167, 21.280833], zoom: 5});',
    '      mapLink = \'<a href="http://openstreetmap.org">OpenStreetMap</a>\';',
    '',
    '      var strmaplayer = L.tileLayer(',
    '        \'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png\', {',
    '        attribution: \'&copy; \' + mapLink + \' Contributors\',',
    '        maxZoom: 18,',
    '      }).addTo(map);',
    '',
    '      var positron = L.tileLayer(\'http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png\', {',
    '        attribution: \'�OpenStreetMap, �CartoDB\',',
    '      });',
    '',
    '      var Esri_OceanBasemap = L.tileLayer(\'http://server.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}\', {',
    '        attribution: \'Tiles &copy; Esri &mdash; Sources: GEBCO, NOAA, CHS, OSU, UNH, CSUMB, National Geographic, DeLorme, NAVTEQ, and Esri\',',
    '        maxZoom: 13',
    '      });',
    '',
    '      var Esri_WorldTopoMap = L.tileLayer(\'http://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}\', {',
    '        attribution: \'Sources: Esri, HERE, Garmin, Intermap, increment P Corp., GEBCO, USGS, FAO, NPS, NRCAN, GeoBase, IGN, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), (c) OpenStreetMap contributors, and the GIS User Community\',',
    '        maxZoom: 13',
    '      });',
    '',
    '      var Esri_WorldStreetMap = L.tileLayer(\'http://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}\', {',
    '        attribution: \'Sources: Esri, HERE, Garmin, USGS, Intermap, INCREMENT P, NRCan, Esri Japan, METI, Esri China (Hong Kong), Esri Korea, Esri (Thailand), NGCC, (c) OpenStreetMap contributors, and the GIS User Community\',',
    '        maxZoom: 13',
    '      });',
    '',
    '      var opentopo = L.tileLayer(\'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png\', {',
    '        attribution: \'�OpenStreetMap, �CartoDB\',',
    '      });',
    '',
    '      var bathymetryLayer = L.tileLayer.wms("http://ows.emodnet-bathymetry.eu/wms", {',
    '        layers: \'emodnet:mean_atlas_land\',',
    '        format: \'image/png\',',
    '        transparent: true,',
    '        attribution: "Emodnet bathymetry",',
    '        opacity: 0.8',
    '      });',
    '',
    '      var coastlinesLayer = L.tileLayer.wms("http://ows.emodnet-bathymetry.eu/wms", {',
    '        layers: \'coastlines\',',
    '        format: \'image/png\',',
    '        transparent: true,',
    '        attribution: "Emodnet bathymetry",',
    '        opacity: 0.8',
    '      });',
    '',
    '      var bathymetryGroupLayer = L.layerGroup([bathymetryLayer, coastlinesLayer]);',
    '',
    '      var contourLayer = L.tileLayer.wms("http://ows.emodnet-bathymetry.eu/wms", {',
    '        layers: \'emodnet:contours\',',
    '        format: \'image/png\',',
    '        transparent: true,',
    '        attribution: "Emodnet bathymetry",',
    '        opacity: 0.8',
    '      });',
    '',
    '      var depthcontours = L.layerGroup([contourLayer]);',
    '',
    '      L.Control.MousePosition = L.Control.extend({',
    '        options: {',
    '          position: \'bottomleft\',',
    '          separator: \'<br>\',',
    '          emptyString: \'Cursor coordinates<br>0&deg;N<br>0&deg;E\',',
    '          lngFirst: false,',
    '          numDigits: 5,',
    '          lngFormatter: function(num) {',
    '            var direction = (num < 0) ? \'W\' : \'E\';',
    '            var degzero = (num < 10) ? \'0\' : \'\';',
    '            var minzero = ((Math.abs(num)-Math.abs(Math.trunc(num)))*60 < 10) ? \'0\' : \'\';',
    '            var formatted = degzero + Math.abs(L.Util.formatNum(num, 5)) + \'&deg; \' + direction + \' = \' + degzero + Math.abs(Math.trunc(num)) + \'&deg; \' + minzero + L.Util.formatNum((Math.abs(num)-Math.abs(Math.trunc(num)))*60,2) + \'&lsquo; \' + direction;',
    '            return formatted;',
    '          },',
    '          latFormatter: function(num) {',
    '            var direction = (num < 0) ? \'S\' : \'N\';',
    '            var degzero = (num < 10) ? \'0\' : \'\';',
    '            var minzero = ((Math.abs(num)-Math.abs(Math.trunc(num)))*60 < 10) ? \'0\' : \'\';',
    '            var formatted = degzero + Math.abs(L.Util.formatNum(num, 5)) + \'&deg; \' + direction + \' = \' + degzero + Math.abs(Math.trunc(num)) + \'&deg; \' + minzero + L.Util.formatNum((Math.abs(num)-Math.abs(Math.trunc(num)))*60,2) + \'&lsquo; \' + direction;',
    '            return formatted;',
    '          },',
    '          prefix: \'<h4 style="color: #0000CC;">Cursor position</h4>\'',
    '        },',
    '',
    '        onAdd: function (map) {',
    '          this._container = L.DomUtil.create(\'div\', \'leaflet-control-mouseposition\');',
    '          L.DomEvent.disableClickPropagation(this._container);',
    '          map.on(\'mousemove\', this._onMouseMove, this);',
    '//          this._container.innerHTML=this.options.emptyString;',
    '          return this._container;',
    '        },',
    '',
    '        onRemove: function (map) {',
    '          map.off(\'mousemove\', this._onMouseMove)',
    '        },',
    '',
    '        _onMouseMove: function (e) {',
    '          var lng = this.options.lngFormatter ? this.options.lngFormatter(e.latlng.lng) : L.Util.formatNum(e.latlng.lng, this.options.numDigits);',
    '          var lat = this.options.latFormatter ? this.options.latFormatter(e.latlng.lat) : L.Util.formatNum(e.latlng.lat, this.options.numDigits);',
    '          var value = this.options.lngFirst ? lng + this.options.separator + lat : lat + this.options.separator + lng;',
    '          var prefixAndValue = this.options.prefix + value;',
    '//          this._container.innerHTML = prefixAndValue;',
    '          cursorinfo._div.innerHTML = prefixAndValue;',
    '',
    '        }',
    '      });',
    '',
    '      var fairways = new L.LayerGroup();',
    '      var fairWays =',
    '        L.tileLayer.wms(\'https://extranet.liikennevirasto.fi/inspirepalvelu/avoin/wms\', {',
    '          layers: \'vaylat,vaylaalueet\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          maxZoom: 18,',
    '          minZoom: 7,',
    '          attribution: \'CC 4.0 Liikennevirasto. Ei navigointikäyttöön. Ei täytä virallisen merikartan vaatimuksia.\',',
    '      }).addTo(fairways);',
    '',
    '      var depthpoints = new L.LayerGroup();',
    '      var depthPoints =',
    '        L.tileLayer.wms(\'https://extranet.liikennevirasto.fi/inspirepalvelu/rajoitettu/wms\', {',
    '          layers: \'syvyyspiste_p\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          maxZoom: 18,',
    '          minZoom: 12,',
    '          attribution: \'CC 4.0 Liikennevirasto. Ei navigointikäyttöön. Ei täytä virallisen merikartan vaatimuksia.\',',
    '      }).addTo(depthpoints);',
    '',
    '      var eez = new L.LayerGroup();',
    '      var eeZ =',
    '        L.tileLayer.wms(\'http://geo.vliz.be/geoserver/MarineRegions/wms\', {',
    '          layers: \'eez_boundaries\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          attribution: \'Marineregions.org.\',',
    '      }).addTo(eez);',
    '',
    '      var internalwaters = new L.LayerGroup();',
    '      var internalWaters =',
    '        L.tileLayer.wms(\'http://geo.vliz.be/geoserver/MarineRegions/wms\', {',
    '          layers: \'eez_internal_waters\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          attribution: \'Marineregions.org.\',',
    '      }).addTo(internalwaters);',
    '',
    '      var internalwaters12 = new L.LayerGroup();',
    '      var internalWaters12 =',
    '        L.tileLayer.wms(\'http://geo.vliz.be/geoserver/MarineRegions/wms\', {',
    '          layers: \'eez_12nm\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          attribution: \'Marineregions.org.\',',
    '      }).addTo(internalwaters12);',
    '',
    '      var helcomareaboundaries = new L.LayerGroup();',
    '      var helcomAreaboundaries =',
    '        L.tileLayer.wms(\'https://maps.helcom.fi/arcgis/services/MADS/Sea_environmental_monitoring/MapServer/WmsServer\', {',
    '          layers: \'89\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          attribution: \'HELCOM.\',',
    '      }).addTo(helcomareaboundaries);',
    '',
    '      var helcomareas = new L.LayerGroup();',
    '      var helcomAreas =',
    '        L.tileLayer.wms(\'https://maps.helcom.fi/arcgis/services/MADS/Sea_environmental_monitoring/MapServer/WmsServer\', {',
    '          layers: \'88\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          attribution: \'HELCOM.\',',
    '      }).addTo(helcomareas);',
    '',
    '      var mNavAttr = \'--- Merikorttipalvelu perustuu Liikenneviraston tuottaman rasterimuotoiseen merikartta-aineistoon. Käyttölupa CC 4.0\'',
    '        +\' Lähde: Liikennevirasto. Ei navigointikäyttöön. Ei täytä virallisen merikartan vaatimuksia.\';',
    '',
    '      var navigate = new L.LayerGroup();',
    '      var Navigate     =',
    '        L.tileLayer.wms(\'https://julkinen.traficom.fi/s57/wms\', {',
    '          layers: \'cells\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          minZoom: 9,',
    '          attribution: mNavAttr',
    '      }).addTo(navigate);',
    '',
    '      var mllAttr =\' Maanmittauslaitoksen nimipalvelu\';',
    '      var nimet = new L.LayerGroup();',
    '      var Nimet =',
    '        L.tileLayer.wms(\'https://inspire-wms.maanmittauslaitos.fi/inspire-wms/GN/wms\', {',
    '          layers: \'GN.GeographicalNames\',',
    '          transparent: true,',
    '          format: \'image/png\',',
    '          minzoom: 5,',
    '          attribution: mllAttr',
    '      }).addTo(nimet);',
    '',
    '      var openseamap = new L.LayerGroup();',
    '      var openSeaMap =',
    '        L.tileLayer(\'http://tiles.openseamap.org/seamark/{z}/{x}/{y}.png\', {minZoom: 6}).addTo(openseamap);',
    '',
    '      L.Map.mergeOptions({positionControl: false});',
    '',
    '      L.Map.addInitHook(function () {',
    '        if (this.options.positionControl) {',
    '          this.positionControl = new L.Control.MousePosition();',
    '          this.addControl(this.positionControl);',
    '        }',
    '      });',
    '',
    '      L.control.mousePosition = function (options) {return new L.Control.MousePosition(options);};',
    '      L.control.mousePosition().addTo(map);',
    '',
    '      info.addTo(map);',
    '      cursorinfo.addTo(map);',
    '      legend.addTo(map);',
    '',
    '//    Stations and route line are on the map by default, other layers not',
    '      stationPoints.addTo(map);',
    '      routeLine.addTo(map);',
    '',
    '      var baseMaps = {',
    '        "StreetMap"             : strmaplayer,',
    '        "Positron"              : positron,',
    '        "ESRI OceanBasemap"     : Esri_OceanBasemap,',
    '        "ESRI Worl_Topo_Map"    : Esri_WorldTopoMap,',
    '        "ESRI World_Street_Map" : Esri_WorldStreetMap,',
    '        "Topo"                  : opentopo',
    '      }',
    '',
    '      var overlayMaps = {',
    '        "EMODnet Bathymetry"            : bathymetryGroupLayer,',
    '        "EMODnet depth contours"        : depthcontours,',
    '        "EEZ"                           : eez,',
    '        "Internal waters"               : internalwaters,',
    '        "Internal waters 12 nm"         : internalwaters12,',
    '        "HELCOM areas"                  : helcomareas,',
    '        "HELCOM area boundaries"        : helcomareaboundaries,',
    '        "Open seamap"                   : openseamap,',
    '        "Finnish fairways"              : fairways,',
    '        "Finnish navigation chart"      : navigate,',
    '        "Finnish depthpoints"           : depthpoints,',
    '        "Latitude-longitude grid"       : latlongrid,',
    '        "Stations of the cruise"        : stationPoints,',
    '        "Routeline of the cruise"       : routeLine,',
    '        "Animated route of the cruise"  : antLine,',
    '        "Paikannimet"                   : nimet',
    '      }',
    '',
    '      L.control.layers(baseMaps, overlayMaps).addTo(map);',
    '',
    '    </script>',
    '  </body>',
    '</html>']


def mcx2leaflethtml(filename):
#=============================
    if '.MKX' in filename.upper():
        acruise = MKXfile(filename)
    else:
        acruise = MCXfile(filename)
    
    [lo1,la1,lo2,la2] = acruise.get_boundingbox()
    
    #with open('MyCruise_Leaflet_Routemap_template_variable_size.html','r') as f:
    #    tmpl = f.read().split('\n')
     
    tmpl = mcx_html_tmpl
        
    for I in range(len(tmpl)):
        if '<title>' in tmpl[I]:
            tmpl[I] = '    <title>Routemap of '+acruise.name_en+'</title>'
            
        if 'var map = L.map' in tmpl[I]:
            tmpl[I] = '      var map = L.map(\'map\', {center:[' \
                + '{:10.6f}'.format((la1+la2)/2) \
                + ', ' \
                + '{:11.6f}'.format((lo1+lo2)/2) \
                + '], zoom: 5});'
            
        if 'Cruise route of' in tmpl[I]:
    #        tmpl[I] = tmpl[I].split('</h4>')[0] \
            tmpl[I] = '        this._div.innerHTML = \'<h4 style="color: #0000CC;">Cruise route of' \
                + ' the ' \
                + acruise.platform_name \
                + ' cruise ' \
                + acruise.nro \
                + '/' \
                + str(acruise.year) \
                + '</h4>' \
                + acruise.name_en \
                + '<br>' \
                + acruise.departure_time.split('T')[0] \
                + ' - ' \
                + acruise.arrival_time.split('T')[0] \
                + '\';'
        if '//pisteet ja reitti' in tmpl[I]:
            I1 = I
            I2 = I+1
    
    olist = []
    
    for I in range(0,I1):
        olist.append(tmpl[I])
    
    olist.append('')
    olist.append('      var stationPoints = L.layerGroup();')
    olist.append('')
    
    for I in range(len(acruise.route)):
        if acruise.route[I].name == 'P':
            continue
        nameandtime = str(I)+': '+acruise.route[I].name+', '+acruise.route[I].entry+', '+'{:5.1f} {}'.format(acruise.route[I].distance,'nmi')
        
        if acruise.route[I].country == 'Finland':
            pColor = 'green'
        else:
            pColor = 'red'
    
        r = '      L.circle([' \
            + '{:9.6f}'.format(acruise.route[I].lat) \
            + ', ' \
            + '{:11.6f}'.format(acruise.route[I].lon) \
            + '], 500, {' \
            + 'color: \'' \
            + pColor \
            + '\',fillColor: \'' \
            + pColor \
            + '\',fillOpacity: 0.5' \
            + '}).addTo(stationPoints).bindTooltip("' \
            + nameandtime \
            + '\");' 
        olist.append(r)
    
    olist.append(' ')
    olist.append('      var routeLine = L.layerGroup();')
    olist.append('      var antLine   = L.layerGroup();')
    olist.append('')
    
    rLine = '      route = ['
    for I in range(len(acruise.route)-1):
        rLine = rLine + '['+'{:9.5f}'.format(acruise.route[I].lat) \
        + ', ' \
        + '{:10.5f}'.format(acruise.route[I].lon) \
        + '],'
    rLine = rLine + '['+'{:9.5f}'.format(acruise.route[-1].lat) + ', ' + '{:10.5f}'.format(acruise.route[-1].lon) + ']]'
    
                     
    olist.append(rLine)
    
    olist.append('      L.polyline(route, {color: \'blue\', weight: 1}).addTo(routeLine);')
    olist.append(' ')
    
    olist.append('      antroute = L.polyline.antPath(route, {')
    olist.append('          "delay": 1000,')
    olist.append('          "dashArray": [10,10],')
    olist.append('          "weight": 3,')
    olist.append('          "color": "#0000FF",')
    olist.append('          "pulseColor": "#FFFFFF",')
    olist.append('          "paused": false ,')
    olist.append('          "reverse": false ,')
    olist.append('          "hardwareAccelerated": true')
    olist.append('      }).addTo(antLine)')
    olist.append(' ')
    
    for I in range(I2,len(tmpl)):
        olist.append(tmpl[I])
    
    o_name = filename.split('.')[0]+'.html'
    o_file = open(o_name,'w')
    for i in range(len(olist)):
        o_file.write(olist[i]+'\n')
    o_file.close()
    print('Valmis! Tulostettu tiedosto '+o_name)     
#=================


class Participant:
    first_name = ''
    last_name = ''
    nationality = ''
    institute = ''
    isquest = False
    tt = False
    isboss = False
    role = ''
    projects = []
    cabin_no = ''
    lab_no = ''
    cabin_phone = ''
    boarding_time = ''
    exit_time = ''
    boarding_harbour = ''
    exit_harbour = ''
    isboardingwithcruise = True
    isleavingwithcruise = True
    def __init__(self, first_name, family_name):  
        self.first_name = first_name  
        self.family_name = family_name 


class Sciencecrew:
    participants = []


class Routepoint:
    name = ''
    lat = 0.0
    lon = 0.0
    depth = 0.0
    point_type = ''
    arrival_time = ''
    departure_time = ''
    duration = 0.0
    observations = []
    isvisited = False
    baseindex = 0
    speedfrom = 10.0
    selected = False
    isarrivalgiven = False
    isspeedcalculated = False
    mapsymbol = 0
    mapsymbol_size = 0
    mapsymbol_color = 0
    comment = ''
    SDN_P02_parameters = ''
    SDN_C77_data = ''
    mooring = False
    mooring_function = ''
    country = ''
    sea_area = ''
    def __init__(self, name, lat, lon):  
        self.name = name  
        self.lat = lat
        self.lon = lon


class Cruiseroute:
    default_speed_knots = 10.0
    default_duration_hours = 0.5
    default_observations = []
    routepoints = []
    language = ''
    default_mapsymbol = 0
    default_mapsymbol_size = 0
    default_mapsymbol_color = 0
    routeline_color = 0
    isscheduled = False
    default_SDN_P02_parameters = []
    default_SDN_C77_data = []


class MCXfile:
    name_fi = ''
    name_en = ''
    ship_name = ''
    ship_code = ''
    ship_master = ''
    nro = 0
    year = 0
    organiser = ''
    scientific_crew = []
    route = []
    status = ''
    plandatetime = ''
    timezonediff = 0
    letterid = ''
    aim_fi = []
    aim_en  = []
    project = ''
    ctdname = ''
    language = ''
    softwareversion = ''
    departure_time = ''
    departure_timezone = ''
    departure_port = ''
    arrival_time = ''
    arrival_timezone = ''
    arrival_port = ''
    header_errors = []

    def __init__(self,fname):
        self.fname = fname
        self.name = ''
        self.organiser = ''
        self.nro = 0
        self.year = 0
        self.status = ''
        self.plandatetime = ''
        self.timezonediff = 0
        self.letterid = ''
        self.name_fi = ''
        self.name_en = ''
        self.aim_fi = ''
        self.aim_en = ''
        self.project = ''
        self.ctd_name = ''
        self.scientific_crew = []
        self.route = []
        self.language = ''
        self.software_version = ''
        self.master = ''
        self.ship_name = ''
        self.ship_code = ''
        self.ship_master = ''
        self.departure_time = ''
        self.departure_timezone = ''
        self.departure_port = ''
        self.arrival_time = ''
        self.arrival_timezone = ''
        self.arrival_port = ''

        my_file = Path(fname)
        if my_file.is_file():
            self.read()
            self.OK = True
        else:
            self.OK = False
            print('\nNOTE! File '+fname+' not found!')
    
    def read(self):
        # read the mcx-file into mcx-object
        cruise = ET.parse(self.fname).getroot()

        cruise_attributes = cruise.attrib
        self.organiser = cruise_attributes['organiser']
        self.name_fi = cruise_attributes['name']
        self.name_en = cruise_attributes['nameEN']
        self.nro = cruise_attributes['nro']
        self.platform_name = cruise_attributes['platformname']
        self.collate_center = cruise_attributes['collateCenter']
        self.platform_code = cruise_attributes['platformcode']
        self.platform_class = cruise_attributes['platform_class']
        self.project = cruise_attributes['project']
        self.plan_status = cruise_attributes['status']
        self.plan_datetime = cruise_attributes['planDateTime']
        self.plan_language = cruise_attributes['language']

        self.software_version = cruise.find("software").get('version')
        
        ship = cruise.find("ship")
        self.ship_name = ship.get('name')
        self.ship_code = ship.get('platformcode')
        self.ship_master = ship.get('master')

        departure = cruise.find('departure')
        self.departure_time  = departure.get('dateTime')
        self.departure_timezone = departure.get('timeZone')
        self.departure_port = departure.get('harbour')

        arrival = cruise.find('arrival')
        self.arrival_time  = arrival.get('dateTime')
        self.arrival_timezone = arrival.get('timeZone')
        self.arrival_port = arrival.get('harbour')

        self.purpose = cruise.find('purpose').text

        # Description of the cruise in English and in Finnish
        description_en = cruise.find('description')
        description_fi= cruise.find('descriptionFIN')
        self.aim_en  = []
        for row in description_en.findall('dr'):
            self.aim_en.append(row.text)
        self.aim_fi  = []
        for row in description_fi.findall('drf'):
            self.aim_fi.append(row.text)

        self.year = 0
        self.timezonediff = 0
        self.letterid = ''
        self.ctd_name = ''

        # get scientific crew
        self.scientific_crew = []
        staff = cruise.find("staff")
        for person in staff.findall("person"):
            member = Participant(person.attrib['firstName'],person.attrib['familyName'])
            member.organisation = person.attrib['organisation']
            member.infixed = person.attrib['inFixed']
            member.indate = person.attrib['inDate']
            member.outfixed = person.attrib['outFixed']
            member.outdate = person.attrib['outDate']
            if person.find('role') != None:
                member.role = person.find('role').text
            if person.find('project') != None:
                member.project = person.find('project').text
            cabin = person.find('cabin').attrib
            member.cabin_no = cabin['nro']
            member.cabin_phone = cabin['phone']
            lab = person.find('lab').attrib
            member.lab_no = lab['nro']
            member.lab_phone = lab['phone']
 
            self.scientific_crew.append(member)

        # Get cruise route
        croute = cruise.find("route")

        defaults = croute.find('defaults')
        self.default_speed_knots = float(defaults.find('speed').text)

        hm = defaults.find('duration').text[1:]
        if 'H' in hm and 'M' in hm:
            h = float(hm.split('H')[0]) + float(hm.split('H')[1].split('M')[0])/60
        elif 'H' in hm:
            h = float(hm.split('H')[0])
        elif 'M' in hm:
            h = float(hm.split('M')[0])/60
        else:
            h = 1.0
        self.default_duration_hours = h
        
        if defaults.find('observations') != None:
            ocode = defaults.find('observations')
            if ocode.find('obscode') != None:
                self.default_observations = ocode.find('obscode').text
        
        self.default_mapsymbol = defaults.find('mapsymbol').attrib

        # Get routepoints
        stations = croute.find("points")
        for station in stations.findall("point"):
            la = station.find('lat').text.split('D')
            lat =float(la[0])+float(la[1].split('M')[0])/60
            lo = station.find('lon').text.split('D')
            lon = float(lo[0])+float(lo[1].split('M')[0])/60
            
            rpoint = Routepoint(station.find('name').text,lat,lon)

            rpoint.nro = station.attrib['nro']
            rpoint.type = station.attrib['type']
            rpoint.status = station.attrib['status']
            rpoint.index = station.attrib['index']
            
            rpoint.depth = float(station.find('depth').text)
            rpoint.distance = float(station.find('distance').text)
            rpoint.entry = station.find('entry').attrib['dateTime']
            rpoint.entry_status = station.find('entry').attrib['status']
            dur = station.find('duration').text[1:]
            rpoint.duration = dur
            rpoint.exit = station.find('exit').attrib['dateTime']
            rpoint.exit_status = station.find('exit').attrib['status']
            rpoint.speed = float(station.find('speed').text)
            rpoint.speed_status = station.find('speed').attrib['status']

            if station.find('observations') != None:
                ocode = station.find('observations')
                if ocode.find('obscode') != None:
                    rpoint.observations = ocode.find('obscode').text

            if station.find('SDN_P02_parameters') != None:
                rpoint.SDN_P02_parameters = station.find('SDN_P02_parameters').text
            
            if station.find('SDN_C77_data') != None:
                rpoint.SDN_C77_data = station.find('SDN_C77_data').text
            
            rpoint.country = station.find('Country').text
            rpoint.sea_area = station.find('SeaArea').text
            rpoint.mooring = child_node_text(station,'isMooring')
            rpoint.mapsymbol = station.find('mapsymbol').attrib
            rpoint.comments = child_node_text(station,'comments')

            self.route.append(rpoint)

        if cruise.find('acquisitionInfo') != None:
            # jotain
            self.acquisitionInfo = cruise.find('acquisitionInfo').text

        if cruise.find('accesPolicies') != None:
            self.accessPolicies = cruise.find('accesPolicies').text

        if cruise.find('dataPaths') != None:
            datapaths = cruise.find('dataPaths')
            if datapaths.find('MKXsave') != None:
                if datapaths.find('MKXsave').attrib['value'] == 'false':
                    self.mkxsave = False
                else:
                    self.mkxsave = True

        self.mapfiles = []
        for mf in cruise.findall('mapfiles'):
            if mf != None:
                self.mapfiles.append(mf.text)
        
        if self.name_en == '':
            self.name_en = self.name_fi

    def get_persons_in_role(self,a_role):
        result = []
        for person in self.scientific_crew:
            if a_role in person.role:
                result.append(person.family_name+' '+person.first_name)
        return result

    def who_is(self,a_role):
        result = 'none'
        for person in self.scientific_crew:
            if a_role in person.role:
                result = person.family_name+' '+person.first_name
        return result

    def get_chief_scientist(self):
        result = self.who_is('chief scientist')
        return result

    def get_chief_chemist(self):
        result = self.who_is('chief chemist')
        return result

    def get_IT_chief(self):
        result = self.who_is('IT-chief')
        return result

    def get_lat(self):
        lat = []
        for station in self.route:
            lat.append(station.lat)
        return lat

    def get_boundingbox(self):
        result = [180.0,90,-180.0,-90.0]
        lat = []
        lon = []
        for station in self.route:
            lat.append(station.lat)
            lon.append(station.lon)
        result = [min(lon),min(lat),max(lon),max(lat)]
        return result   

    def leaflethtml(self):
    #=====================
        [lo1,la1,lo2,la2] = self.get_boundingbox()
        llhtml = mcx_html_tmpl.copy()
        for I in range(len(llhtml)):
            if '<title>' in llhtml[I]:
                llhtml[I] = '    <title>Routemap of '+self.name_en+'</title>'
                
            if 'var map = L.map' in llhtml[I]:
                llhtml[I] = '      var map = L.map(\'map\', {center:[' \
                    + '{:10.6f}'.format((la1+la2)/2) \
                    + ', ' \
                    + '{:11.6f}'.format((lo1+lo2)/2) \
                    + '], zoom: 5});'
                
            if 'Cruise route of' in llhtml[I]:
        #        tmpl[I] = tmpl[I].split('</h4>')[0] \
                llhtml[I] = '        this._div.innerHTML = \'<h4 style="color: #0000CC;">Cruise route of' \
                    + ' the ' \
                    + self.platform_name \
                    + ' cruise ' \
                    + self.nro \
                    + '/' \
                    + str(self.year) \
                    + '</h4>' \
                    + self.name_en \
                    + '<br>' \
                    + self.departure_time.split('T')[0] \
                    + ' - ' \
                    + self.arrival_time.split('T')[0] \
                    + '\';'
            if '//pisteet ja reitti' in llhtml[I]:
                I1 = I
                I2 = I+1
        
        olist = []
        
        for I in range(0,I1):
            olist.append(llhtml[I])
        
        olist.append('')
        olist.append('      var stationPoints = L.layerGroup();')
        olist.append('')
        
        for I in range(len(self.route)):
            if self.route[I].name == 'P':
                continue
            nameandtime = str(I)+': '+self.route[I].name+', '+self.route[I].entry+', '+'{:5.1f} {}'.format(self.route[I].distance,'nmi')
            
            if self.route[I].country == 'Finland':
                pColor = 'green'
            else:
                pColor = 'red'
        
            r = '      L.circle([' \
                + '{:9.6f}'.format(self.route[I].lat) \
                + ', ' \
                + '{:11.6f}'.format(self.route[I].lon) \
                + '], 500, {' \
                + 'color: \'' \
                + pColor \
                + '\',fillColor: \'' \
                + pColor \
                + '\',fillOpacity: 0.5' \
                + '}).addTo(stationPoints).bindTooltip("' \
                + nameandtime \
                + '\");' 
            olist.append(r)
        
        olist.append(' ')
        olist.append('      var routeLine = L.layerGroup();')
        olist.append('      var antLine   = L.layerGroup();')
        olist.append('')
        
        rLine = '      route = ['
        for I in range(len(self.route)-1):
            rLine = rLine + '['+'{:9.5f}'.format(self.route[I].lat) \
            + ', ' \
            + '{:10.5f}'.format(self.route[I].lon) \
            + '],'
        rLine = rLine + '['+'{:9.5f}'.format(self.route[-1].lat) + ', ' + '{:10.5f}'.format(self.route[-1].lon) + ']]'
        
                         
        olist.append(rLine)
        
        olist.append('      L.polyline(route, {color: \'blue\', weight: 1}).addTo(routeLine);')
        olist.append(' ')
        
        olist.append('      antroute = L.polyline.antPath(route, {')
        olist.append('          "delay": 1000,')
        olist.append('          "dashArray": [10,10],')
        olist.append('          "weight": 3,')
        olist.append('          "color": "#0000FF",')
        olist.append('          "pulseColor": "#FFFFFF",')
        olist.append('          "paused": false ,')
        olist.append('          "reverse": false ,')
        olist.append('          "hardwareAccelerated": true')
        olist.append('      }).addTo(antLine)')
        olist.append(' ')
        
        for I in range(I2,len(llhtml)):
            olist.append(llhtml[I])
        
        o_name = self.fname.split('.')[0]+'.html'
        o_file = open(o_name,'w')
        for i in range(len(olist)):
            o_file.write(olist[i]+'\n')
        o_file.close()
        print('Valmis! Tulostettu tiedosto '+o_name) 
        return    

class MKXfile:
    name = ''
    name_en = ''
    ship_name = ''
    ship_code = ''
    ship_master = ''
    nro = 0
    year = 0
    organiser = ''
    scientific_crew = []
    route = []
    status = ''
    plandatetime = ''
    timezonediff = 0
    letterid = ''
    aim_fi = []
    aim_en  = []
    project = ''
    ctdname = ''
    language = ''
    softwareversion = ''
    departure_time = ''
    departure_timezone = ''
    departure_port = ''
    arrival_time = ''
    arrival_timezone = ''
    arrival_port = ''
    header_errors = []

    def __init__(self,fname):
        self.fname = fname
        self.name = ''
        self.organiser = ''
        self.nro = 0
        self.year = 0
        self.status = ''
        self.plandatetime = ''
        self.timezonediff = 0
        self.letterid = ''
        self.name_fi = ''
        self.name_en = ''
        self.aim_fi = ''
        self.aim_en = ''
        self.project = ''
        self.ctd_name = ''
        self.scientific_crew = []
        self.route = []
        self.language = ''
        self.software_version = ''
        self.master = ''
        self.platform_name = ''
        self.platform_code = ''
        self.ship_name = ''
        self.ship_code = ''
        self.ship_master = ''
        self.departure_time = ''
        self.departure_timezone = ''
        self.departure_port = ''
        self.arrival_time = ''
        self.arrival_timezone = ''
        self.arrival_port = ''

        my_file = Path(fname)
        if my_file.is_file():
            self.read()
            self.OK = True
        else:
            self.OK = False
    
    def read(self):
        # read the mcx-file into mcx-object
        cruise = ET.parse(self.fname).getroot()

        cruise_attributes = cruise.attrib
        self.organiser = cruise_attributes['organiser']
        self.name_fi = cruise_attributes['name']
        self.name_en = cruise_attributes['nameEN']
        self.nro = cruise_attributes['nro']
#        self.platform_name = cruise_attributes['platformname']
#        self.collate_center = cruise_attributes['collateCenter']
#        self.platform_code = cruise_attributes['platformcode']
#        self.platform_class = cruise_attributes['platform_class']
        self.project = cruise_attributes['project']
        self.plan_status = cruise_attributes['status']
        self.plan_datetime = cruise_attributes['planDateTime']
        self.plan_language = cruise_attributes['language']

        self.software_version = cruise.find("software").get('version')
        
        ship = cruise.find("ship")
        self.ship_name = ship.get('name')
        self.ship_code = ship.get('platformcode')
        self.ship_master = ship.get('master')

        departure = cruise.find('departure')
        self.departure_time  = departure.get('dateTime')
        self.departure_timezone = departure.get('timeZone')
        self.departure_port = departure.get('harbour')

        arrival = cruise.find('arrival')
        self.arrival_time  = arrival.get('dateTime')
        self.arrival_timezone = arrival.get('timeZone')
        self.arrival_port = arrival.get('harbour')

        # Description of the cruise in English and in Finnish
        description_en = cruise.find('description')
        description_fi= cruise.find('descriptionFIN')
        self.aim_en  = []
        for row in description_en.findall('dr'):
            self.aim_en.append(row.text)
        self.aim_fi  = []
        for row in description_fi.findall('drf'):
            self.aim_fi.append(row.text)

        self.year = 0
        self.timezonediff = 0
        self.letterid = ''
        self.ctd_name = ''

        # get scientific crew
        self.scientific_crew = []
        staff = cruise.find("staff")
        for person in staff.findall("person"):
            member = Participant(person.attrib['firstName'],person.attrib['familyName'])
            member.organisation = person.attrib['institute']
            member.infixed = person.attrib['inFixed']
            member.indate = person.attrib['inDate']
            member.outfixed = person.attrib['outFixed']
#            member.outdate = person.attrib['outDate']
            if person.find('role') != None:
                member.role = person.find('role').text
            if person.find('project') != None:
                member.project = person.find('project').text
            cabin = person.find('cabin').attrib
            member.cabin_no = cabin['nro']
            member.cabin_phone = cabin['phone']
            lab = person.find('lab').attrib
            member.lab_no = lab['nro']
            member.lab_phone = lab['phone']
 
            self.scientific_crew.append(member)

        # Get cruise route
        croute = cruise.find("route")

        defaults = croute.find('defaults')
        self.default_speed_knots = float(defaults.find('speed').text)

        hm = defaults.find('duration').text[1:]
        if 'H' in hm and 'M' in hm:
            h = float(hm.split('H')[0]) + float(hm.split('H')[1].split('M')[0])/60
        elif 'H' in hm:
            h = float(hm.split('H')[0])
        elif 'M' in hm:
            h = float(hm.split('M')[0])/60
        else:
            h = 1.0
        self.default_duration_hours = h
        
        if defaults.find('observations') != None:
            ocode = defaults.find('observations')
            if ocode.find('obscode') != None:
                self.default_observations = ocode.find('obscode').text
        
        self.default_mapsymbol = defaults.find('mapsymbol').attrib

        # Get routepoints
        stations = croute.find("points")
        for station in stations.findall("point"):
            la = station.find('lat').text.split('D')
            lat =float(la[0])+float(la[1].split('M')[0])/60
            lo = station.find('long').text.split('D')
            lon = float(lo[0])+float(lo[1].split('M')[0])/60
            
            rpoint = Routepoint(station.find('name').text,lat,lon)

            rpoint.nro = station.attrib['nro']
            rpoint.type = station.attrib['type']
            rpoint.status = station.attrib['status']
            rpoint.index = station.attrib['index']
            
            rpoint.depth = float(station.find('depth').text)
            rpoint.distance = float(station.find('distance').text)
            rpoint.entry = station.find('entry').attrib['dateTime']
#            rpoint.entry_status = station.find('entry').attrib['status']
            dur = station.find('duration').text[1:]
            rpoint.duration = dur
            rpoint.exit = station.find('exit').attrib['dateTime']
            rpoint.exit_status = station.find('exit').attrib['status']
            rpoint.speed = float(station.find('speed').text)
            rpoint.speed_status = station.find('speed').attrib['status']

            if station.find('observations') != None:
                ocode = station.find('observations')
                if ocode.find('obscode') != None:
                    rpoint.observations = ocode.find('obscode').text

            if station.find('SDN_P02_parameters') != None:
                rpoint.SDN_P02_parameters = station.find('SDN_P02_parameters').text
            
            if station.find('SDN_C77_data') != None:
                rpoint.SDN_C77_data = station.find('SDN_C77_data').text
            
            if station.find('Country') != None:
                rpoint.country = station.find('Country').text
            if station.find('SeaArea') != None:
                rpoint.sea_area = station.find('SeaArea').text
            if child_node_text(station,'isMooring') != None:
                rpoint.mooring = child_node_text(station,'isMooring')
            if station.find('mapsymbol') != None:
                rpoint.mapsymbol = station.find('mapsymbol').attrib
            if child_node_text(station,'comments') != None:
                rpoint.comments = child_node_text(station,'comments')

            self.route.append(rpoint)

        if cruise.find('acquisitionInfo') != None:
            # jotain
            self.acquisitionInfo = cruise.find('acquisitionInfo').text

        if cruise.find('accesPolicies') != None:
            self.accessPolicies = cruise.find('accesPolicies').text

        if cruise.find('dataPaths') != None:
            datapaths = cruise.find('dataPaths')
            if datapaths.find('MKXsave') != None:
                if datapaths.find('MKXsave').attrib['value'] == 'false':
                    self.mkxsave = False
                else:
                    self.mkxsave = True

        self.mapfiles = []
        for mf in cruise.findall('mapfiles'):
            if mf != None:
                self.mapfiles.append(mf.text)
        
        if self.name_en == '':
            self.name_en = self.name_fi

    def get_persons_in_role(self,a_role):
        result = []
        for person in self.scientific_crew:
            if a_role in person.role:
                result.append(person.family_name+' '+person.first_name)
        return result

    def who_is(self,a_role):
        result = 'none'
        for person in self.scientific_crew:
            if a_role in person.role:
                result = person.family_name+' '+person.first_name
        return result

    def get_chief_scientist(self):
        result = self.who_is('chief scientist')
        return result

    def get_chief_chemist(self):
        result = self.who_is('chief chemist')
        return result

    def get_IT_chief(self):
        result = self.who_is('IT-chief')
        return result

    def get_lat(self):
        lat = []
        for station in self.route:
            lat.append(station.lat)
        return lat

    def get_boundingbox(self):
        result = [180.0,90,-180.0,-90.0]
        lat = []
        lon = []
        for station in self.route:
            lat.append(station.lat)
            lon.append(station.lon)
        result = [min(lon),min(lat),max(lon),max(lat)]
        return result

    def leaflethtml(self):
    #=====================
        [lo1,la1,lo2,la2] = self.get_boundingbox()        
        llhtml = mcx_html_tmpl.copy()
        for I in range(len(llhtml)):
            if '<title>' in llhtml[I]:
                llhtml[I] = '    <title>Routemap of '+self.name_en+'</title>'
                
            if 'var map = L.map' in llhtml[I]:
                llhtml[I] = '      var map = L.map(\'map\', {center:[' \
                    + '{:10.6f}'.format((la1+la2)/2) \
                    + ', ' \
                    + '{:11.6f}'.format((lo1+lo2)/2) \
                    + '], zoom: 5});'
                
            if 'Cruise route of' in llhtml[I]:
        #        tmpl[I] = tmpl[I].split('</h4>')[0] \
                llhtml[I] = '        this._div.innerHTML = \'<h4 style="color: #0000CC;">Cruise route of' \
                    + ' the ' \
                    + self.platform_name \
                    + ' cruise ' \
                    + self.nro \
                    + '/' \
                    + str(self.year) \
                    + '</h4>' \
                    + self.name_en \
                    + '<br>' \
                    + self.departure_time.split('T')[0] \
                    + ' - ' \
                    + self.arrival_time.split('T')[0] \
                    + '\';'
            if '//pisteet ja reitti' in llhtml[I]:
                I1 = I
                I2 = I+1
        
        olist = []
        
        for I in range(0,I1):
            olist.append(llhtml[I])
        
        olist.append('')
        olist.append('      var stationPoints = L.layerGroup();')
        olist.append('')
        
        for I in range(len(self.route)):
            if self.route[I].name == 'P':
                continue
            nameandtime = str(I)+': '+self.route[I].name+', '+self.route[I].entry+', '+'{:5.1f} {}'.format(self.route[I].distance,'nmi')
            
            if self.route[I].country == 'Finland':
                pColor = 'green'
            else:
                pColor = 'red'
        
            r = '      L.circle([' \
                + '{:9.6f}'.format(self.route[I].lat) \
                + ', ' \
                + '{:11.6f}'.format(self.route[I].lon) \
                + '], 500, {' \
                + 'color: \'' \
                + pColor \
                + '\',fillColor: \'' \
                + pColor \
                + '\',fillOpacity: 0.5' \
                + '}).addTo(stationPoints).bindTooltip("' \
                + nameandtime \
                + '\");' 
            olist.append(r)
        
        olist.append(' ')
        olist.append('      var routeLine = L.layerGroup();')
        olist.append('      var antLine   = L.layerGroup();')
        olist.append('')
        
        rLine = '      route = ['
        for I in range(len(self.route)-1):
            rLine = rLine + '['+'{:9.5f}'.format(self.route[I].lat) \
            + ', ' \
            + '{:10.5f}'.format(self.route[I].lon) \
            + '],'
        rLine = rLine + '['+'{:9.5f}'.format(self.route[-1].lat) + ', ' + '{:10.5f}'.format(self.route[-1].lon) + ']]'
        
                         
        olist.append(rLine)
        
        olist.append('      L.polyline(route, {color: \'blue\', weight: 1}).addTo(routeLine);')
        olist.append(' ')
        
        olist.append('      antroute = L.polyline.antPath(route, {')
        olist.append('          "delay": 1000,')
        olist.append('          "dashArray": [10,10],')
        olist.append('          "weight": 3,')
        olist.append('          "color": "#0000FF",')
        olist.append('          "pulseColor": "#FFFFFF",')
        olist.append('          "paused": false ,')
        olist.append('          "reverse": false ,')
        olist.append('          "hardwareAccelerated": true')
        olist.append('      }).addTo(antLine)')
        olist.append(' ')
        
        for I in range(I2,len(llhtml)):
            olist.append(llhtml[I])
        
        o_name = self.fname.split('.')[0]+'.html'
        o_file = open(o_name,'w', encoding="utf-8")
        for i in range(len(olist)):
            o_file.write(olist[i]+'\n')
        o_file.close()
        print('Valmis! Tulostettu tiedosto '+o_name) 
        return    
