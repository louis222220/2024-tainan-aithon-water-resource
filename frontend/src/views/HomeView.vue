<script setup>
import MapView from '../components/MapView.vue';
</script>

<template>
  <main>
    <div class = 'wrap-map' >
      <MapView />
    </div>
  </main>
</template>

<style scoped>
.wrap-map {
  width: 100vw;
  height: 100vh;
  max-width: 1200px;
}
</style>