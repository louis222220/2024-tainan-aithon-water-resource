<template>
  <div>
    <div id="map"></div>
    <button @click="sendPolygon" class="send-button">確定22</button>
  </div>
</template>

<script>
import { onMounted, ref, onBeforeUnmount } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { sendCoordinate } from '../api/coordinate';

export default {
  name: 'MapView',
  setup() {
    const map = ref(null);
    const markers = ref([]);
    const polygon = ref(null);

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
    const sendPolygon = async () => {
      if (!polygon.value) return;

      const latlngs = markers.value.map(({ marker }) => marker.getLatLng());
      const wktPolygon = `POLYGON((${latlngs.map(latlng => `${latlng.lng} ${latlng.lat}`).join(', ')}))`;

      const payload = {
        overlap_ratio: 0.8, // 假設這是固定值，你可以根據需要進行修改
        wkt_polygon: wktPolygon
      };

      try {
        const response = await sendCoordinate(payload);
        console.log('Polygon sent successfully:', response);
      } catch (error) {
        console.error('錯誤資訊阿:', error);
        alert('發送多邊形時發生錯誤，請聯繫管理員。');
        throw new Error('發送多邊形時發生錯誤，請聯繫管理員。');
      }
    };

    return {
      map,
      markers,
      polygon,
      clearPolygon,
      sendPolygon
    };
  }
};
</script>

<style scoped>
#map {
  width: 100%;
  height: 100vh;
}
.send-button {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1000;
}
</style>