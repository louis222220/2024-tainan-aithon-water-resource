# 將外部公開資料傳入PostGis
import pandas as pd
from pyproj import Transformer
from sqlalchemy import create_engine
import geopandas as gpd
from shapely.geometry import Point


# 建立資料庫引擎函數
def CreateSQLEngine():

    # 設定資料庫連接資訊
    host = "127.0.0.1"
    database = "postgres"
    user = "postgres"
    password = "admin"
    port = "5432"

    # 建立資料庫引擎
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")

    return engine


# 整理臺南市門牌座標資料函數
def ImportHouseNumData(engine):

    # 讀取門牌座標資料
    houseNumData = pd.read_csv('112年臺南市門牌坐標資料.csv')

    # 建立經緯度轉換器
    transformer = Transformer.from_crs("EPSG:3826", "EPSG:4326", always_xy=True)

    # 定義轉換函數
    def convert_to_wgs84(row):
        return Point(transformer.transform(row['橫座標'], row['縱座標']))

    # 將門牌座標由TWD97轉為WGS84格式
    houseNumData['geometry'] = houseNumData.apply(convert_to_wgs84, axis=1)

    # 移除不需要的欄位
    houseNumData = houseNumData.drop(columns=['橫座標', '縱座標'])

    # 重新命名欄位
    houseNumData.columns = [
        'city_code', 'dist_code', 'village', 'neighborhood',
        'road_street', 'area', 'lane', 'alley', 'number',
        'geometry'
    ]

    # 轉為geopandas格式
    houseNumData = gpd.GeoDataFrame(houseNumData, geometry='geometry')
    # 設定座標系統
    houseNumData.crs = 'EPSG:4326'

    # 匯入資料至資料庫
    houseNumData.to_postgis('house_num', con=engine, if_exists='replace')

    return houseNumData


# 匯入臺南市人口統計資料函數
def ImportPopulationData(engine):

    # 讀取Geojson檔案
    fileName = '112年12月臺南市統計區人口統計_最小統計區_WGS84.geojson'
    populationData = gpd.read_file(fileName)
    populationData.columns = populationData.columns.str.lower()

    # 匯入資料至資料庫
    populationData.to_postgis('population', con=engine, if_exists='replace')
    
    return populationData


# 自PostGIS資料庫讀取資料
def GetPostGISData(engine, tableName):
    gdf = gpd.read_postgis(tableName, con=engine, geom_col='geometry')
    return gdf


# 主程式
if __name__ == '__main__':

    # 建立資料庫引擎
    engine = CreateSQLEngine()

    # 整理臺南市門牌座標資料
    ImportHouseNumData(engine)

    # 整理臺南市人口統計資料
    ImportPopulationData(engine)

    # 自PostGIS資料庫讀取臺南市門牌座標資料
    houseNumData = GetPostGISData(engine, 'house_num')

    # 自PostGIS資料庫讀取臺南市人口統計資料
    populationData = GetPostGISData(engine, 'population')