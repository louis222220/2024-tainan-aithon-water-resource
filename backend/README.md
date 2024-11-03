# 2024台南黑客松-水利局災害影響評估平台

## 後台部署流程
* 共有3個容器一同部署
    * db: PostGIS資料庫
    * db_init: 以Python程式匯入初始資料(人口與門牌至資料庫)，啟動後須等待一段時間匯入
    * fastapi: Python FastAPI
* 在本專案的backen資料夾目錄下，以Docker-compose部署指令:
```
cd backend
docker-compose up -d
```

## Python
* 使用Python 3.11版本
* 安裝套件清單請參考`requirements.txt`
* 部署FastAPI與匯入初始資料使用

## PostGIS
* 以Docker建立PostGIS服務
* [PostGIS Docker官方頁面](https://registry.hub.docker.com/r/postgis/postgis/)
* Image使用`postgis/postgis:17-3.5`
* 連線方式:
    * host: 127.0.0.1
    * database: postgres
    * user: postgres
    * password: admin
    * port: 5432
* 資料表:
    * households: 112年臺南市門牌坐標資料
    * population: 112年12月臺南市統計區人口統計_最小統計區_WGS84

## FastAPI
* 預計提供給前台使用，目前設計6個API接口:
    * /households/point: 計算指定點半徑範圍內的家戶數 
        * 輸入: 指定點經緯度、半徑(公尺)
        * 輸出: 家戶數
    * /population/point: 計算指定點半徑範圍內的人口數
        * 輸入: 指定點經緯度、半徑(公尺)、與最小區域重疊範圍比率
        * 輸出: 人口數
    * /households/area: 計算指定多邊形範圍內的家戶數
        * 輸入: 多邊形經緯度
        * 輸出: 家戶數
    * /population/area: 計算指定多邊形範圍內的人口數
        * 輸入: 多邊形經緯度、與最小區域重疊範圍比率
        * 輸出: 人口數
    * /tables/create: 建立標註資料表
        * 輸入: 資料表名、欄位型別
        * 輸出: 無
    * /tables/delete: 刪除標註資料表
        * 輸入: 資料表名
        * 輸出: 無
    * /tables/{table_name}/insert: 新增資料至資料表
        * 輸入: 資料表名、欄位數值
        * 輸出: 無
    * 備註:
        * 多邊形經緯度格式範例: POLYGON((120.1828 22.9961, 120.1811 22.9869, 120.1906 22.9926, 120.1828 22.9961))
        * 與最小區域重疊範圍比率: 介於0至1之間

* 使用說明與測試請參考FastAPI頁面: [http://127.0.0.1:8000/docs#/](http://127.0.0.1:8000/docs#/)


