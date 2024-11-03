/* PostGIS使用範例 */

/*查詢臺南市門牌資料*/
SELECT * FROM public.households;

/*查詢臺南是最小行政區人口資料*/
SELECT * FROM public.population;

/*查詢指定點半徑範圍內門牌數*/
SELECT count(*) as householdNums
FROM households
WHERE ST_DWithin(
	geography(ST_SetSRID(ST_Point(120.1854, 22.9921), 4326)),
	geography(geometry),
	200 --半徑範圍(公尺)
);

/*查詢指定多邊形範圍內的門牌資料*/
SELECT *
FROM households
WHERE ST_Within(
	geometry, 
	ST_GeomFromText('POLYGON((120.1828 22.9961, 120.1811 22.9869, 120.1906 22.9926, 120.1828 22.9961))', 4326));

/*查詢指定點半徑範圍內的最小行政區資料*/
WITH 
target_point AS (
    SELECT ST_SetSRID(ST_MakePoint(120.1854, 22.9921), 4326) AS geom
),
buffered_area AS (
    SELECT ST_Buffer(ST_Transform(geom, 3857), 300) AS geom  -- 將點轉換到3857座標系進行緩衝區計算 半徑範圍設為300公尺
    FROM target_point
)
SELECT 
	population.*,
    ST_Area(ST_Intersection(ST_Transform(population.geometry, 3857), buffered_area.geom)) AS intersection_area,  -- 計算重疊面積
    ST_Area(ST_Transform(population.geometry, 3857)) AS population_area,  -- 計算population區域的面積
    (ST_Area(ST_Intersection(ST_Transform(population.geometry, 3857), buffered_area.geom)) / ST_Area(ST_Transform(population.geometry, 3857))) AS overlap_ratio  -- 計算重疊比率
FROM population
JOIN buffered_area ON ST_Intersects(ST_Transform(population.geometry, 3857), buffered_area.geom)
WHERE (ST_Area(ST_Intersection(ST_Transform(population.geometry, 3857), buffered_area.geom)) / ST_Area(ST_Transform(population.geometry, 3857))) >= 0.8;  -- 0.8為重疊比率門檻 超過此門檻才會被選入

/*查詢指定點半徑範圍內的人口數*/
WITH 
target_point AS (
    SELECT ST_SetSRID(ST_MakePoint(120.1854, 22.9921), 4326) AS geom
),
buffered_area AS (
    SELECT ST_Buffer(ST_Transform(geom, 3857), 300) AS geom  -- 將點轉換到3857座標系進行緩衝區計算 半徑範圍設為300公尺
    FROM target_point
)
SELECT sum(population.p_cnt) as population
FROM population
JOIN buffered_area ON ST_Intersects(ST_Transform(population.geometry, 3857), buffered_area.geom)
WHERE (ST_Area(ST_Intersection(ST_Transform(population.geometry, 3857), buffered_area.geom)) / ST_Area(ST_Transform(population.geometry, 3857))) >= 0.8;  -- 0.8為重疊比率門檻 超過此門檻才會被選入

/*查詢指定多邊形範圍內的人口數*/
WITH 
input_polygon AS (
    SELECT ST_SetSRID(ST_GeomFromText('POLYGON((120.1828 22.9961, 120.1811 22.9869, 120.1906 22.9926, 120.1828 22.9961))'), 4326) AS geom
)
SELECT sum(population.p_cnt) as population
FROM population
JOIN input_polygon ON ST_Intersects(ST_Transform(population.geometry, 3857), ST_Transform(input_polygon.geom, 3857))
WHERE (ST_Area(ST_Intersection(ST_Transform(population.geometry, 3857), ST_Transform(input_polygon.geom, 3857))) / ST_Area(ST_Transform(population.geometry, 3857))) >= 0.8;
