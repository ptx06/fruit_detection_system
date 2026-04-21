<template>
  <div id="app">
    <DetectionView />
  </div>
</template>

<script setup lang="ts">
import DetectionView from './views/DetectionView.vue'
</script>

<style>
body {
  margin: 0;
  background-color: #f5f7fa;
}
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}
</style>