<template>
  <div class="annotated-image-container" ref="containerRef" :style="{ maxWidth: maxWidth + 'px' }">
    <canvas ref="canvasRef" style="display: block;" />
    <div v-if="!imageLoaded" class="placeholder">图片加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'

interface DetectionBox {
  bbox: number[]  // [x1, y1, x2, y2]
  fruit_type: string
  maturity?: string
  confidence?: number
  fruit_conf?: number
  maturity_conf?: number
}

const props = defineProps<{
  imageSrc: string           // 支持 base64 或 URL
  detections: DetectionBox[]
  maxWidth?: number          // 容器最大宽度，默认 600
}>()

const containerRef = ref<HTMLElement>()
const canvasRef = ref<HTMLCanvasElement>()
const canvasWidth = ref(0)
const canvasHeight = ref(0)
const imageLoaded = ref(false)

const drawCanvas = async () => {
  if (!canvasRef.value || !props.imageSrc) return

  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  console.log('Drawing canvas with detections:', props.detections)

  // 加载图片
  const img = new Image()
  img.src = props.imageSrc
  
  img.onload = () => {
    console.log('Image loaded successfully, starting to draw')
    imageLoaded.value = true
    // 计算绘制尺寸（保持比例，适应容器宽度）
    const maxW = props.maxWidth || 600
    const scale = Math.min(maxW / img.width, 1)
    canvasWidth.value = img.width * scale
    canvasHeight.value = img.height * scale
    canvas.width = canvasWidth.value
    canvas.height = canvasHeight.value

    // 绘制原图
    ctx.drawImage(img, 0, 0, canvasWidth.value, canvasHeight.value)
    console.log('Drew original image')

    // 绘制所有检测框
    console.log('Number of detections:', props.detections.length)
    props.detections.forEach((det, index) => {
      console.log('Processing detection', index, det)
      // 确保bbox存在且格式正确
      if (!det.bbox || det.bbox.length !== 4) {
        console.warn('Invalid bbox for detection', index, det)
        return
      }
      
      const [x1, y1, x2, y2] = det.bbox
      console.log('Original bbox:', x1, y1, x2, y2)
      // 缩放坐标
      const scaledX1 = x1 * scale
      const scaledY1 = y1 * scale
      const scaledX2 = x2 * scale
      const scaledY2 = y2 * scale
      console.log('Scaled bbox:', scaledX1, scaledY1, scaledX2, scaledY2)

      // 根据水果类型设置颜色
      let color = '#00ff00'
      if (det.fruit_type === 'apple') color = '#ff4d4f'
      else if (det.fruit_type === 'banana') color = '#fadb14'
      else if (det.fruit_type === 'orange') color = '#fa8c16'

      // 绘制矩形框
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.strokeRect(scaledX1, scaledY1, scaledX2 - scaledX1, scaledY2 - scaledY1)

      // 绘制标签背景
      const confidence = det.fruit_conf || det.confidence
      const label = `${det.fruit_type} ${det.maturity || ''} ${confidence ? (confidence * 100).toFixed(0) + '%' : ''}`
      ctx.font = '14px Arial'
      const textWidth = ctx.measureText(label).width
      ctx.fillStyle = color
      ctx.fillRect(scaledX1, scaledY1 - 22, textWidth + 10, 22)

      // 绘制标签文字
      ctx.fillStyle = '#ffffff'
      ctx.fillText(label, scaledX1 + 5, scaledY1 - 6)
      console.log('Drew detection', index)
    })
    console.log('Finished drawing all detections')
  }
  
  img.onerror = (error) => {
    console.error('Error loading image:', error)
    imageLoaded.value = false
  }
}

onMounted(() => {
  drawCanvas()
})

watch(() => [props.imageSrc, props.detections], () => {
  // 重置图片加载状态，确保重新绘制
  imageLoaded.value = false
  nextTick(() => drawCanvas())
}, { deep: true })
</script>

<style scoped>
.annotated-image-container {
  position: relative;
  display: inline-block;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}
canvas {
  display: block;
}
.placeholder {
  padding: 20px;
  text-align: center;
  color: #999;
}
</style>