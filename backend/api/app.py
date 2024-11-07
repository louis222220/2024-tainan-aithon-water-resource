from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from pydantic import BaseModel
from typing import List
import os
from fastapi.middleware.cors import CORSMiddleware

# 設定 FastAPI 應用程式
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 資料庫連線設定 
host = os.getenv("DB_HOST", "127.0.0.1")
database = "postgres"
user = "postgres"
password = "admin"
port = "5432"
engine = create_async_engine(f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# 欄位型別模型
class ColumnType(BaseModel):
    name: str  # 欄位名稱
    type: str  # 資料型別

# 欄位內容模型
class ColumnValue(BaseModel):
    name: str  # 欄位名稱
    value: str  # 資料內容

# 請求建立資料表模型
class CreateTableRequest(BaseModel):
    table_name: str  # 資料表名稱
    columns: List[ColumnType]  # 欄位型別

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "table_name": "example_table",
                    "columns": [
                        {"name": "id", "type": "SERIAL"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "households", "type": "INTEGER"},
                        {"name": "population", "type": "INTEGER"},
                        {"name": "geometry", "type": "geometry(Polygon, 4326)"},
                    ]
                }
            ]
        }
    }

# 請求刪除資料表模型
class DeleteTableRequest(BaseModel):
    table_name: str  # 資料表名稱

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "table_name": "example_table",
                }
            ]
        }
    }

# 請求新增資料模型
class InsertDataRequest(BaseModel):
    table_name: str  # 資料表名稱
    columns: List[ColumnValue]  # 欄位內容

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "table_name": "example_table",
                    "columns": [
                        {"name": "name", "value": "測試項目1"},
                        {"name": "households", "value": "50"},
                        {"name": "population", "value": "100"},
                        {"name": "geometry", "value": "POLYGON((120.1828 22.9961, 120.1811 22.9869, 120.1906 22.9926, 120.1828 22.9961))"},
                    ]
                }
            ]
        }
    }

# 請求單點模型
class PointRequest(BaseModel):
    longitude: float  # 經度
    latitude: float  # 緯度
    radius: float  # 單位為公尺
    overlap_ratio: float = Query(0.8, ge=0, le=1)  # 重疊面積比率門檻 超過此門檻才會被納入計算 預設為80%

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "longitude": 120.1854,
                    "latitude": 22.9921,
                    "radius": 500,
                    "overlap_ratio": 0.8
                }
            ]
        }
    }

# 請求面積模型
class PolygonRequest(BaseModel):
    wkt_polygon: str  # Well-Known Text 格式的多邊形 例如: POLYGON((x1 y1, x2 y2, x3 y3, x1 y1))
    overlap_ratio: float = Query(0.8, ge=0, le=1)  # 重疊面積比率門檻 超過此門檻才會被納入計算 預設為80%

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "wkt_polygon": "POLYGON((120.1828 22.9961, 120.1811 22.9869, 120.1906 22.9926, 120.1828 22.9961))",
                    "overlap_ratio": 0.8
                }
            ]
        }
    }

# 回傳家戶數模型
class HouseholdsResponse(BaseModel):
    households: int  # 家戶數量

# 回傳人口數模型 (如果需要的話，這裡簡單示範，實際上可能需要更複雜的邏輯)
class PopulationResponse(BaseModel):
    population: int  # 人口數量


# 首頁
@app.get("/", response_class=HTMLResponse)
async def index():
    return '''
    <p>API測試請至此連結: <a href="http://127.0.0.1:8000/docs#/">http://127.0.0.1:8000/docs#/</a><p>
    '''


# 建立資料表
@app.post("/tables/create", response_model=str)
async def create_table(request: CreateTableRequest):
    async with SessionLocal() as session:
        try:
            # 構建 SQL 查詢以建立資料表
            columns = ", ".join([f"{col.name} {col.type}" for col in request.columns])
            query = f"CREATE TABLE IF NOT EXISTS {request.table_name} ({columns});"
            await session.execute(text(query))
            await session.commit()
            return f"Table '{request.table_name}' created successfully."
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# 刪除資料表
@app.delete("/tables/delete/", response_model=str)
async def delete_table(request: DeleteTableRequest):
    async with SessionLocal() as session:
        try:
            # 構建 SQL 查詢以刪除資料表
            query = f"DROP TABLE IF EXISTS {request.table_name};"
            await session.execute(text(query))
            await session.commit()
            return f"Table '{request.table_name}' deleted successfully."
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        

# 新增資料
@app.post("/tables/{table_name}/insert", response_model=str)
async def insert_data(request: InsertDataRequest):
    async with SessionLocal() as session:
        try:
            # 構建 SQL 查詢以插入資料
            columns = ", ".join([f"{col.name}" for col in request.columns])
            values = ''
            for col in request.columns:
                if col.name == 'geometry':
                    values = values + f"ST_GeomFromText('{col.value}', 4326), "
                else:
                    values = values + f"'{col.value}', "
            values = values[0:-2]  # 移除最後逗號
            query = f"INSERT INTO {request.table_name} ({columns}) VALUES ({values});"
            await session.execute(text(query))
            await session.commit()
            return f"Data inserted into '{request.table_name}' successfully."
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
# 刪除資料

# 查詢資料

# 修改資料


# 計算單點半徑範圍內家戶數
@app.post("/households/point", response_model=HouseholdsResponse)
async def get_households_within_radius(request: PointRequest):
    async with SessionLocal() as session:
        try:
            # 使用 PostGIS 查詢範圍內的戶數
            query = text("""       
                SELECT count(*) as households
                FROM households
                WHERE ST_DWithin(
                    geography(ST_SetSRID(ST_Point(:longitude, :latitude), 4326)),
                    geography(geometry),
                    :radius
                );
            """)
            result = await session.execute(query, {
                "longitude": request.longitude,
                "latitude": request.latitude,
                "radius": request.radius
            })
            data = result.fetchone()

            if data:
                return HouseholdsResponse(households=data.households or 0)
            else:
                raise HTTPException(status_code=404, detail="No data found within the specified radius")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# 計算單點半徑範圍內人口數
@app.post("/population/point", response_model=PopulationResponse)
async def get_population_within_radius(request: PointRequest):
    async with SessionLocal() as session:
        try:
            # 使用 PostGIS 查詢範圍內的人口數
            query = text("""
                WITH 
                target_point AS (
                    SELECT ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326) AS geom
                ),
                buffered_area AS (
                    SELECT ST_Buffer(ST_Transform(geom, 3857), :radius) AS geom
                    FROM target_point
                )
                SELECT sum(population.p_cnt) as population
                FROM population
                JOIN buffered_area ON ST_Intersects(ST_Transform(population.geometry, 3857), buffered_area.geom)
                WHERE (ST_Area(ST_Intersection(ST_Transform(population.geometry, 3857), buffered_area.geom)) / ST_Area(ST_Transform(population.geometry, 3857))) >= :overlap_ratio;
            """)
            result = await session.execute(query, {
                "longitude": request.longitude,
                "latitude": request.latitude,
                "radius": request.radius,
                "overlap_ratio": request.overlap_ratio,
            })
            data = result.fetchone()

            if data:
                return PopulationResponse(population=data.population or 0)
            else:
                raise HTTPException(status_code=404, detail="No data found within the specified radius")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# 計算多點面積範圍內家戶數
@app.post("/households/area", response_model=HouseholdsResponse)
async def get_households_within_polygon(request: PolygonRequest):
    async with SessionLocal() as session:
        try:
            # 使用 PostGIS 查詢範圍內的戶數
            query = text("""
                SELECT count(*) as households
                FROM households
                WHERE ST_Within(
                    geometry, 
                    ST_GeomFromText(:wkt_polygon, 4326));
            """)
            result = await session.execute(query, {
                "wkt_polygon": request.wkt_polygon,
            })
            data = result.fetchone()

            if data:
                return HouseholdsResponse(households=data.households or 0)
            else:
                raise HTTPException(status_code=404, detail="No data found within the specified area")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# 計算多點面積範圍內人口數
@app.post("/population/area", response_model=PopulationResponse)
async def get_households_within_polygon(request: PolygonRequest):
    async with SessionLocal() as session:
        try:
            # 使用 PostGIS 查詢範圍內的人口數
            query = text("""
                WITH 
                input_polygon AS (
                    SELECT ST_SetSRID(ST_GeomFromText(:wkt_polygon), 4326) AS geom
                )
                SELECT sum(population.p_cnt) as population
                FROM population
                JOIN input_polygon ON ST_Intersects(ST_Transform(population.geometry, 3857), ST_Transform(input_polygon.geom, 3857))
                WHERE (ST_Area(ST_Intersection(ST_Transform(population.geometry, 3857), ST_Transform(input_polygon.geom, 3857))) / ST_Area(ST_Transform(population.geometry, 3857))) >= :overlap_ratio;
            """)
            result = await session.execute(query, {
                "wkt_polygon": request.wkt_polygon,
                "overlap_ratio": request.overlap_ratio,
            })
            data = result.fetchone()

            if data:
                return PopulationResponse(population=data.population or 0)
            else:
                raise HTTPException(status_code=404, detail="No data found within the specified area")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# 主程式
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
