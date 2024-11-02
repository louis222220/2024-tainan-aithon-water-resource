# 2024台南黑客松-水利局災害影響評估平台

# Python
* 使用Python 3.11.9版本
* 安裝套件清單請參考`requirements.txt`

# PostGIS
* 以Docker建立PostGIS服務
* [PostGIS Docker官方頁面](https://registry.hub.docker.com/r/postgis/postgis/)
* Image使用`postgis/postgis:17-3.5`
* Docker部署指令:
```
docker run --name postgis --env=POSTGRES_PASSWORD=admin -p 5432:5432 -d postgis/postgis:17-3.5
```