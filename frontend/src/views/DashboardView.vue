<template>
  <div class="dashboard">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card">
      <div class="welcome-content">
        <h2>欢迎回来，{{ authStore.userInfo?.username }}！</h2>
        <p>{{ currentDate }}</p>
      </div>
    </el-card>
    <el-button v-if="authStore.userInfo?.role === 'admin'" type="warning" @click="$router.push('/admin')">
  用户管理
    </el-button>
    <el-button v-if="authStore.userInfo?.role === 'admin'" @click="$router.push('/admin/settings')">
  系统设置
    </el-button>
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon primary">
            <span class="icon-text">📷</span>
          </div>
          <div class="stat-content">
            <div class="stat-label">总检测次数</div>
            <div class="stat-value">{{ stats.total_detections }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon success">
            <span class="icon-text">🍎</span>
          </div>
          <div class="stat-content">
            <div class="stat-label">总水果数量</div>
            <div class="stat-value">{{ stats.total_fruits }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon warning">
            <span class="icon-text">📊</span>
          </div>
          <div class="stat-content">
            <div class="stat-label">水果种类数</div>
            <div class="stat-value">{{ fruitTypeCount }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon danger">
            <span class="icon-text">📈</span>
          </div>
          <div class="stat-content">
            <div class="stat-label">今日检测</div>
            <div class="stat-value">{{ todayDetections }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card header="水果种类分布" shadow="hover">
          <div ref="fruitChartRef" style="height: 300px; width: 100%"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="成熟度分布" shadow="hover">
          <div ref="maturityChartRef" style="height: 300px; width: 100%"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <el-card header="近7天检测趋势" shadow="hover">
          <div ref="trendChartRef" style="height: 300px; width: 100%"></div>
        </el-card>
      </el-col>
    </el-row>
    <!-- 模型信息 -->
    <el-row :gutter="20" class="model-info">
      <el-col :span="24">
        <el-card header="当前模型信息" shadow="hover">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="检测模型">
              {{ modelInfo.detection.name }} {{ modelInfo.detection.version }}
            </el-descriptions-item>
            <el-descriptions-item label="检测准确率">
              {{ modelInfo.detection.accuracy }}
            </el-descriptions-item>
            <el-descriptions-item label="分类模型">
              MobileNetV2 (苹果/香蕉/橘子)
            </el-descriptions-item>
            <el-descriptions-item label="分类准确率">
              苹果: {{ modelInfo.classification.apple.accuracy }}<br>
              香蕉: {{ modelInfo.classification.banana.accuracy }}<br>
              橘子: {{ modelInfo.classification.orange.accuracy }}
            </el-descriptions-item>
            <el-descriptions-item label="模型更新时间">
              检测: {{ modelInfo.detection.last_updated }}<br>
              分类: {{ modelInfo.classification.apple.last_updated }}
            </el-descriptions-item>
            <el-descriptions-item label="说明">
              {{ modelInfo.detection.description }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
    <!-- 快捷操作 -->
    <el-row :gutter="20" class="actions">
      <el-col :span="24">
        <el-card shadow="hover">
          <div class="quick-actions">
            <el-button @click="$router.push('/batch')">批量检测</el-button>
            <el-button type="primary" @click="$router.push('/detection')">开始检测</el-button>
            <el-button @click="$router.push('/history')">查看历史</el-button>
            <el-button @click="$router.push('/profile')">个人中心</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getDashboardStats, type DashboardStats } from '@/api/dashboard'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import { getModelInfo, type ModelInfo } from '@/api/system'

const modelInfo = ref<ModelInfo>({
  detection: { name: '', version: '', accuracy: '', last_updated: '', description: '' },
  classification: { 
    apple: { name: '', version: '', accuracy: '', last_updated: '' },
    banana: { name: '', version: '', accuracy: '', last_updated: '' },
    orange: { name: '', version: '', accuracy: '', last_updated: '' }
  }
})
const authStore = useAuthStore()

const stats = ref<DashboardStats>({
  total_detections: 0,
  total_fruits: 0,
  fruit_distribution: {},
  maturity_distribution: {},
  daily_trend: []
})

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long'
})

const fruitTypeCount = computed(() => Object.keys(stats.value.fruit_distribution).length)
const todayDetections = computed(() => {
  const trend = stats.value.daily_trend
  return trend.length > 0 ? trend[trend.length - 1].count : 0
})

// 图表容器引用
const fruitChartRef = ref<HTMLElement>()
const maturityChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()

let fruitChart: echarts.ECharts | null = null
let maturityChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// 初始化图表
const initCharts = () => {
  if (fruitChartRef.value) {
    fruitChart = echarts.init(fruitChartRef.value)
  }
  if (maturityChartRef.value) {
    maturityChart = echarts.init(maturityChartRef.value)
  }
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
  }
}

// 更新图表数据
const updateCharts = () => {
  if (fruitChart) {
    const fruitOption: EChartsOption = {
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', left: 'left' },
      series: [{
        type: 'pie',
        radius: '50%',
        data: Object.entries(stats.value.fruit_distribution).map(([name, value]) => ({ name, value }))
      }]
    }
    fruitChart.setOption(fruitOption)
  }

  if (maturityChart) {
    const maturityOption: EChartsOption = {
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', left: 'left' },
      series: [{
        type: 'pie',
        radius: '50%',
        data: Object.entries(stats.value.maturity_distribution).map(([name, value]) => ({ name, value }))
      }]
    }
    maturityChart.setOption(maturityOption)
  }

  if (trendChart) {
    const trendOption: EChartsOption = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: stats.value.daily_trend.map(item => item.date),
        axisLabel: { rotate: 45 }
      },
      yAxis: { type: 'value', name: '检测次数' },
      series: [{
        name: '检测次数',
        type: 'line',
        data: stats.value.daily_trend.map(item => item.count),
        smooth: true,
        lineStyle: { color: '#409eff', width: 3 },
        areaStyle: { color: 'rgba(64, 158, 255, 0.1)' }
      }],
      grid: { bottom: 80 }
    }
    trendChart.setOption(trendOption)
  }
}

const fetchStats = async () => {
  try {
    stats.value = await getDashboardStats()
    await nextTick()
    updateCharts()
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

const fetchModelInfo = async () => {
  try {
    modelInfo.value = await getModelInfo()
  } catch (error) {
    console.error('获取模型信息失败', error)
  }
}

onMounted(() => {
  initCharts()
  fetchStats()
  fetchModelInfo()
  window.addEventListener('resize', () => {
    fruitChart?.resize()
    maturityChart?.resize()
    trendChart?.resize()
  })
})

// 清理图表
const cleanup = () => {
  fruitChart?.dispose()
  maturityChart?.dispose()
  trendChart?.dispose()
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}
.welcome-card .welcome-content h2 {
  margin: 0 0 8px 0;
  color: white;
}
.welcome-card .welcome-content p {
  margin: 0;
  opacity: 0.9;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px 0;
}
.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 40px;
}
.stat-icon.primary { background: #e6f7ff; color: #1890ff; }
.stat-icon.success { background: #f6ffed; color: #52c41a; }
.stat-icon.warning { background: #fffbe6; color: #faad14; }
.stat-icon.danger { background: #fff2f0; color: #ff4d4f; }

.icon-text {
  font-size: 36px;
  line-height: 1;
}

.stat-content {
  flex: 1;
}
.stat-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-bottom: 5px;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #262626;
}

.chart-row {
  margin-bottom: 20px;
}

.quick-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>