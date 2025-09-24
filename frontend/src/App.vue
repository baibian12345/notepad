<template>
  <div id="app">
    <!-- 动态背景组件 -->
    <DynamicBackground />
    
    <!-- 主要内容区域 -->
    <div class="main-content">
      <RouterView />
    </div>
  </div>
</template>

<script>
import { RouterView } from 'vue-router'
import DynamicBackground from './components/DynamicBackground.vue'

export default {
  name: 'App',
  components: {
    RouterView,
    DynamicBackground
  }
}
</script>

<style scoped>
#app {
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.main-content {
  position: relative;
  z-index: 10;
  height: 100vh;
}
</style>