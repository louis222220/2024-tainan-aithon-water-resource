<template>
  <div>
    <div id="map"></div>
    <div class="controls">
      <button @click="fetchData" class="send-button">確定</button>
      <div class="instructions">
        <p>按下 ESC 鍵可以取消該次選取範圍。</p>
      </div>
      <div v-if="households !== null && population !== null" class="data-table">
        <table>
          <thead>
            <tr>
              <th>項目</th>
              <th>數量</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>門牌數</td>
              <td>{{ households }}</td>
            </tr>
            <tr>
              <td>人口數</td>
              <td>{{ population }}</td>
            </tr>
            <tr>
              <td>自訂義項目</td>
              <td><input v-model="customField1" type="text" /></td>
            </tr>
            <tr>
              <td>自訂義項目</td>
              <td><input v-model="customField2" type="text" /></td>
            </tr>
            <tr>
              <td>自訂義項目</td>
              <td><input v-model="customField3" type="text" /></td>
            </tr>
            <tr>
              <td colspan="2"><button @click="submitCustomFields">送出</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref, onBeforeUnmount } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { getHouseholds, getPopulation } from '../api/coordinate';

export default {
  name: 'MapView',
  setup() {
    const map = ref(null);
    const markers = ref([]);
    const polygon = ref(null);
    const households = ref(null);  // 新增一個狀態來存儲門牌數
    const population = ref(null);  // 新增一個狀態來存儲人口數
    const customField1 = ref('');  // 新增一個狀態來存儲自訂義欄位1的值
    const customField2 = ref('');  // 新增一個狀態來存儲自訂義欄位2的值
    const customField3 = ref('');  // 新增一個狀態來存儲自訂義欄位3的值

    onMounted(() => {
      map.value = L.map('map').setView([23.0, 120.2], 13);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map.value);

      map.value.on('click', async (e) => {
        const { lat, lng } = e.latlng;
        const address = await getAddress(lat, lng);

        const marker = L.marker(e.latlng).addTo(map.value);
        marker.bindPopup(address).openPopup();

        // 收集座標 & 地址
        markers.value.push({ marker, address, latlng: e.latlng });

        updatePolygon();
      });

      map.value.on('zoomend', () => {
        updateMarkers();
        updatePolygon();
      });

      document.addEventListener('keydown', handleKeyDown);
    });

    onBeforeUnmount(() => {
      document.removeEventListener('keydown', handleKeyDown);
    });

    // 按下esc 清除多邊形
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        clearPolygon();
      }
    };

    // 取得地址
    const getAddress = async (lat, lng) => {
      const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
      const data = await response.json();
      return data.display_name || 'No address found';
    };

    const clearPolygon = () => {
      // 移除多邊形
      if (polygon.value) {
        map.value.removeLayer(polygon.value);
        polygon.value = null;
      }

      // 移除每個標記圖示
      markers.value.forEach(({ marker }) => marker.remove());
      markers.value = [];
    };

    // 更新所有標記的位置
    const updateMarkers = () => {
      markers.value.forEach(({ marker }) => {
        marker.setLatLng(marker.getLatLng());
      });
    };

    // 更新多邊形的形狀
    const updatePolygon = () => {
      if (polygon.value) {
        map.value.removeLayer(polygon.value);
      }

      const latlngs = markers.value.map(({ marker }) => {
        return marker.getLatLng();
      });

      if (latlngs.length > 0) {
        polygon.value = L.polygon(latlngs, { color: 'red' }).addTo(map.value);
      }
    };

    // 發送多邊形座標到後端
    const fetchData = async () => {
      if (!polygon.value) return;

      const latlngs = markers.value.map(({ marker }) => marker.getLatLng());
      // 目前的 API 是頭尾的點要連接起來
      latlngs.push(latlngs[0]);
      const wktPolygon = `POLYGON((${latlngs.map(latlng => `${latlng.lng} ${latlng.lat}`).join(', ')}))`;

      const payload = {
        overlap_ratio: 0.8,
        wkt_polygon: wktPolygon
      };

      try {
        const [householdsResponse, populationResponse] = await Promise.all([
          getHouseholds(payload),
          getPopulation(payload)
        ]);
        households.value = householdsResponse.households;  // 更新門牌數
        population.value = populationResponse.population;  // 更新人口數
      } catch (error) {
        console.error('error:', error);
        alert('發送多邊形時發生錯誤，請聯繫管理員。');
        throw new Error('發送多邊形時發生錯誤，請聯繫管理員。');
      }
    };

    // 送出自訂義欄位的值
    const submitCustomFields = () => {
      //.. 送去後端
      alert('自訂義欄位已送出');
    };

    return {
      map,
      markers,
      polygon,
      households,  // 返回門牌數狀態
      population,  // 返回人口數狀態
      customField1,  // 返回自訂義欄位1的狀態
      customField2,  // 返回自訂義欄位2的狀態
      customField3,  // 返回自訂義欄位3的狀態
      clearPolygon,
      fetchData,
      submitCustomFields  // 返回送出自訂義欄位的函數
    };
  }
};
</script>

<style scoped>
#map {
  width: 100%;
  height: 100vh;
}
.controls {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.send-button {
  padding: 10px 20px;
  background-color: #007bff;
  color: black;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}
.send-button:hover {
  background-color: #0056b3;
}
.data-table {
  background-color: white;
  padding: 10px;
  border: 1px solid black;
  border-radius: 5px;
  color: black;
  font-size: 16px;
}
.data-table table {
  width: 100%;
  border-collapse: collapse;
}
.data-table th, .data-table td {
  border: 1px solid black;
  padding: 8px;
  text-align: left;
}
.data-table th {
  background-color: #f2f2f2;
}
.instructions {
  padding: 10px;
  border-radius: 5px;
  color: red;
  font-size: 14px;
}
</style>