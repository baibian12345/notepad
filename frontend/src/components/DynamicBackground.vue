<template>
  <div class="dynamic-background">
    <!-- 使用Vue3 Lottie播放器 -->
    <Vue3Lottie
      v-if="animationData"
      :animationData="animationData"
      :loop="true"
      :autoPlay="true"
      class="lottie-animation"
    />
    
    <!-- 备用渐变背景 -->
    <div v-else class="fallback-background"></div>
  </div>
</template>

<script>
import { Vue3Lottie } from 'vue3-lottie'

export default {
  name: 'DynamicBackground',
  components: {
    Vue3Lottie
  },
  data() {
    return {
      animationData: null
    }
  },
  async mounted() {
    try {
      // 尝试加载Lottie动画文件
      const response = await fetch('/labubu-background.json')
      if (response.ok) {
        this.animationData = await response.json()
      } else {
        console.log('未找到Lottie动画文件，使用备用背景')
      }
    } catch (error) {
      console.log('加载Lottie动画失败，使用备用背景:', error)
    }
  }
}
</script>

<style scoped>
.dynamic-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1;
  overflow: hidden;
}

.lottie-animation {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.fallback-background {
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    #667eea 0%,
    #764ba2 25%,
    #f093fb 50%,
    #f5576c 75%,
    #4facfe 100%
  );
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}

@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
</style>