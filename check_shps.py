import geopandas as gpd
import os

shp_files = [
    'shp-file/Road_Centre_Line.shp', 
    'shp-file/Water_Body_Line.shp', 
    'shp-file/Utility_Poly.shp', 
    'shp-file/Water_Body.shp', 
    'shp-file/Road.shp', 
    'shp-file/Bridge.shp', 
    'shp-file/Railway.shp', 
    'shp-file/Waterbody_Point.shp'
]

for shp in shp_files:
    path = f'data/raw/v3_shps/{shp}'
    try:
        gdf = gpd.read_file(path)
        print(f'{shp} Columns: {list(gdf.columns)}')
    except Exception as e:
        print(f'{shp} Error: {e}')
