#!/usr/bin/env python
# coding: utf-8

# In[1]:

import os

import rasterio
import geopandas as gpd
import pandas as pd
from shapely import geometry
from shapely.geometry import box
import earthpy.spatial as es

from functools import partial
import pyproj
from shapely.ops import transform

import matplotlib.pyplot as plt

data_path = "./data"

lulc_path = os.path.join(data_path, "lulc/inp.tif")
settlements_path = os.path.join(data_path, "hrsl/hrsl_nga_settlement.tif")
osm_land_use_path = os.path.join(data_path, "osm/gis_osm_landuse_a_free_1.shp")
osm_roads_path = os.path.join(data_path, "osm/gis_osm_roads_free_1.shp")
osm_waterways_path = os.path.join(data_path, "osm/gis_osm_waterways_free_1.shp")
osm_water_path = os.path.join(data_path, "osm/gis_osm_water_a_free_1.shp")
osm_traffic_path = os.path.join(data_path, "osm/gis_osm_traffic_a_free_1.shp")
osm_transport_path = os.path.join(data_path, "osm/gis_osm_transport_a_free_1.shp")

acled_path = os.path.join(data_path, "acled/events.shp")

osm_land_use = gpd.read_file(osm_land_use_path).to_crs("epsg:4326")
osm_roads = gpd.read_file(osm_roads_path).to_crs("epsg:4326")
osm_waterways = gpd.read_file(osm_waterways_path).to_crs("epsg:4326")
osm_water = gpd.read_file(osm_water_path).to_crs("epsg:4326")
osm_traffic = gpd.read_file(osm_traffic_path).to_crs("epsg:4326")
osm_transport = gpd.read_file(osm_transport_path).to_crs("epsg:4326")

acled = gpd.read_file(acled_path).to_crs("epsg:4326")

features = {
    0:{"name":"Unknown", "color":"#f00"},
    7:{"name":"Mangrove", "color":"#33CCCC"},
    15:{"name":"Gallery forest and riparian forest", "color":"#A95CE6"},
    28:{"name":"Swamp forest", "color":"#BEFFA6"},
    2:{"name":"Savanna", "color":"#af7dd0"},
    8:{"name":"Agriculture", "color":"#7eee0a"},
    78:{"name":"Open mine", "color":"#505050"},
    3:{"name":"Wetland - floodplain", "color":"#000080"},
    24:{"name":"Agriculture in bottomlands and flood recessional", "color":"#E7C961"},
    1:{"name":"Forest", "color":"#84008A"},
    10:{"name":"Sandy area", "color":"#FF99CC"},
    12:{"name":"Bare soil", "color":"#A87000"},
    31:{"name":"Herbaceous savanna", "color":"#0A9696"},
    4:{"name":"Steppe", "color":"#FFCC99"},
    27:{"name":"Cropland and fallow with oil palms", "color":"#EBDF73"},
    25:{"name":"Woodland", "color":"#14ecbb"},
    32:{"name":"Shrubland", "color":"#14ecaa"},
    13:{"name":"Settlements", "color":"#7407da"},
    6:{"name":"Plantation", "color":"#7eee0a"},
    11:{"name":"Rocky land", "color":"#3c1833"},
    29:{"name":"Sahelian short grass savanna", "color":"#22ed9c"},
    23:{"name":"Thicket", "color":"#030d3d"},
    5:{"name":"Oasis", "color":"#010596"},
    16:{"name":"Shrub and tree savanna", "color":"#21c5e8"},
    22:{"name":"Bowe", "color":"#a18f77"},
    9:{"name":"Water bodies", "color":"#345efc"},
    21:{"name":"Degraded forest", "color":"#399fa7"},
    14:{"name":"Irrigated agriculture", "color":"#14fb28"}
}


# In[2]:


osm_land_use_idx = osm_land_use.sindex
osm_roads_idx = osm_roads.sindex
osm_waterways_idx = osm_waterways.sindex
osm_water_idx = osm_water.sindex
osm_traffic_idx = osm_traffic.sindex
osm_transport_idx = osm_transport.sindex
acled_idx = acled.sindex 


# In[3]:


def reproject_to_meters(polygon):
    projection = partial(pyproj.transform, pyproj.Proj('epsg:4326'), pyproj.Proj('epsg:3857'))
    projected = transform(projection, polygon)

    return projected

def calculate_area(polygon):
    poly = []
    for p in polygon["coordinates"][0]:
        poly.append([p[0], p[1]])
    
    polygon = geometry.Polygon(poly)
    polygon = reproject_to_meters(polygon)

    area = polygon.area     #polygon is a shapely object, so we can do this

    return area

def polygonize_by_extent(bounding_polygon):
    with rasterio.open(lulc_path) as lulc:
        out_img, out_meta = es.crop_image(lulc, bounding_polygon)

        features_gen = (
            {
                'properties': {
                'DN': v, 
                'feature_name': features[v]["name"],
                'feature_color':features[v]["color"],
                'feature_type':'land cover',
                'feature_desc':'N/A',
                'feature_date':''
#                 'feature_area':calculate_area(s) / 10000
                }, 'geometry': s
            } for i, (s,v) in enumerate(
            rasterio.features.shapes(out_img, None, transform=out_meta["transform"])
        ))

        geometries = list(features_gen)

    with rasterio.open(settlements_path) as path:
        out_img, out_meta = es.crop_image(path, bounding_polygon)
        
        features_gen = (
            {
                'properties': {
                'DN': v, 
                'feature_name': "Building Cluster",
                'feature_color':"#000",
                'feature_type':'Settlement Density',
                'feature_desc':'N/A',
                'feature_date':''
#                 'feature_area':calculate_area(s) / 10000
                }, 'geometry': s
            } for i, (s,v) in enumerate(
            rasterio.features.shapes(out_img, None, transform=out_meta["transform"])
        ))
        
        
        geometries = geometries + list(features_gen)
    
    bounds = list(bounding_polygon.bounds.values[0])
    possible_matches_index = list(osm_land_use_idx.intersection(bounds))
    possible_matches = osm_land_use.loc[possible_matches_index]
    features_gen = (
        {
            'properties': {
            'DN': v["code"], 
            'feature_name': v["fclass"],
            'feature_color':"#ccc",
            'feature_type':'Land Use',
            'feature_desc':'N/A',
            'feature_date':''
            }, 'geometry': v["geometry"]
        } for i, v in possible_matches.iterrows()
    )
    
    geometries = geometries + list(features_gen)
    
    possible_matches_index = list(osm_roads_idx.intersection(bounds))
    possible_matches = osm_roads.loc[possible_matches_index]
    features_gen = (
        {
            'properties': {
            'DN': v["code"], 
            'feature_name': v["fclass"],
            'feature_color':"#f00",
            'feature_type':'Terrain',
            'feature_desc':'N/A',
            'feature_date':''
            }, 'geometry': v["geometry"]
        } for i, v in possible_matches.iterrows()
    )
    
    geometries = geometries + list(features_gen)
    
    possible_matches_index = list(osm_waterways_idx.intersection(bounds))
    possible_matches = osm_waterways.loc[possible_matches_index]
    features_gen = (
        {
            'properties': {
            'DN': v["code"], 
            'feature_name': v["fclass"],
            'feature_color':"#00f",
            'feature_type':'Water Way',
            'feature_desc':'N/A',
            'feature_date':''
            }, 'geometry': v["geometry"]
        } for i, v in possible_matches.iterrows()
    )
    
    geometries = geometries + list(features_gen)
    
    possible_matches_index = list(osm_water_idx.intersection(bounds))
    possible_matches = osm_water.loc[possible_matches_index]
    features_gen = (
        {
            'properties': {
            'DN': v["code"], 
            'feature_name': v["fclass"],
            'feature_color':"#00002f",
            'feature_type':'Water Body',
            'feature_desc':'N/A',
            'feature_date':''
            }, 'geometry': v["geometry"]
        } for i, v in possible_matches.iterrows()
    )
    
    geometries = geometries + list(features_gen)
    
    possible_matches_index = list(osm_transport_idx.intersection(bounds))
    possible_matches = osm_transport.loc[possible_matches_index]
    features_gen = (
        {
            'properties': {
            'DN': v["code"], 
            'feature_name': v["fclass"],
            'feature_color':"#34ff5c",
            'feature_type':'Public Transport',
            'feature_desc':'N/A',
            'feature_date':''
            }, 'geometry': v["geometry"]
        } for i, v in possible_matches.iterrows()
    )
    
    geometries = geometries + list(features_gen)
    
    possible_matches_index = list(osm_traffic_idx.intersection(bounds))
    possible_matches = osm_traffic.loc[possible_matches_index]
    features_gen = (
        {
            'properties': {
            'DN': v["code"], 
            'feature_name': v["fclass"],
            'feature_color':"#003ccc",
            'feature_type':'Urban Traffic',
            'feature_desc':'N/A',
            'feature_date':''
            }, 'geometry': v["geometry"]
        } for i, v in possible_matches.iterrows()
    )
    
    geometries = geometries + list(features_gen)
    
    possible_matches_index = list(acled_idx.intersection(bounds))
    possible_matches = acled.loc[possible_matches_index]
#     print(list(possible_matches))
    features_gen = (
        {
            'properties': {
            'DN': v["EVENT_ID_C"], 
            'feature_name': v["SUB_EVENT_"],
            'feature_color':"#ffccee",
            'feature_type':'OSINT Event',
            'feature_desc':v["NOTES"],
            'feature_date':v["EVENT_DATE"]
            }, 'geometry': v["geometry"]
        } for i, v in possible_matches.iterrows()
    )
    
    geometries = geometries + list(features_gen)
    
    polygonized_features = gpd.GeoDataFrame.from_features(geometries)

    return polygonized_features


# In[5]:


lat_point_list = [12.37689222487227, 12.438588130697482, 12.438588130697482, 12.37689222487227]
lon_point_list = [7.7954864501953125, 7.7954864501953125, 7.889900207519531, 7.889900207519531]
from shapely.geometry import Polygon
polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
crs = {'init': 'epsg:4326'}
polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])  
# print(polygon.head())
res = polygonize_by_extent(polygon)
print(res.head())


# In[ ]:


# from flask import *
# from flask_cors import CORS
# import json
# from shapely.geometry import Polygon

# api = Flask(__name__)
# CORS(api)
# @api.route('/process', methods=['GET', 'POST'])

# def success():
#     if request.method == 'POST':
#         data = request.form["data"]
#         data = json.loads(data)
        
#         lon_list = data["lon"]
#         lat_list = data["lat"]
        
#         res = {}
#     else:
#         lon_list = []
#         lat_list = []
        
#     polygon_geom = Polygon(zip(lon_list, lat_list))
#     crs = {'init': 'epsg:4326'}
#     polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])  

#     res = polygonize_by_extent(polygon)
    
#     return  {"status":1, "result":res.to_json()}

# if __name__ == '__main__':
#     api.run(port=5001)


# # In[ ]:


from flask import *
from flask_cors import CORS

api = Flask(__name__)
CORS(api)
@api.route('/process', methods=['GET', 'POST'])

def success():
    if request.method == 'POST':
        img_path = request.form["url"]
    else:
        img_path = request.args.get("url")
    
    res = polygonize_by_extent(img_path)
    return  {"status":1, "result":res.to_json()}

if __name__ == '__main__':
    api.run(port=5001)


# In[ ]:




