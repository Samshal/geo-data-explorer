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

from rtree.index import Index

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
# osm_roads = gpd.read_file(osm_roads_path).to_crs("epsg:4326")
# osm_waterways = gpd.read_file(osm_waterways_path).to_crs("epsg:4326")
# osm_water = gpd.read_file(osm_water_path).to_crs("epsg:4326")
# osm_traffic = gpd.read_file(osm_traffic_path).to_crs("epsg:4326")
# osm_transport = gpd.read_file(osm_transport_path).to_crs("epsg:4326")

# acled = gpd.read_file(acled_path).to_crs("epsg:4326")

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
# osm_roads_idx = osm_roads.sindex
# osm_waterways_idx = osm_waterways.sindex
# osm_water_idx = osm_water.sindex
# osm_traffic_idx = osm_traffic.sindex
# osm_transport_idx = osm_transport.sindex
# acled_idx = acled.sindex 

idx = Index("./index/osm_land_use_idx")
print("here")
for i,k in list(osm_land_use_idx):
 idx.insert(i, k)
idx.close()
print("Done with osm_land_use_idx")

# idx = Index("./index/osm_roads_idx")
# idx.insert(osm_roads_idx)
# idx.close()
# print("Done with osm_roads_idx")

# idx = Index("./index/osm_waterways_idx")
# idx.insert(osm_waterways_idx)
# idx.close()
# print("Done with osm_waterways_idx")

# idx = Index("./index/osm_water_idx")
# idx.insert(osm_water_idx)
# idx.close()
# print("Done with osm_water_idx")

# idx = Index("./index/osm_traffic_idx")
# idx.insert(osm_traffic_idx)
# idx.close()
# print("Done with osm_traffic_idx")

# idx = Index("./index/osm_transport_idx")
# idx.insert(osm_transport_idx)
# idx.close()
# print("Done with osm_transport_idx")

# idx = Index("./index/acled_idx")
# idx.insert(acled_idx)
# idx.close()
# print("Done with acled_idx")

print("Done")