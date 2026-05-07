<template>
  <div class="ai-summary">
    <el-card class="summary-card">
      <template #header>
        <div class="card-header">
          <span>水果检测分析报告</span>
          <el-button type="primary" @click="generateSummary" :loading="loading">
            生成分析报告
          </el-button>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <el-form :model="form" class="filter-form">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="开始日期">
              <el-date-picker
                v-model="form.start_date"
                type="date"
                placeholder="选择开始日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="结束日期">
              <el-date-picker
                v-model="form.end_date"
                type="date"
                placeholder="选择结束日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="水果类型">
              <el-select
                v-model="form.fruit_types"
                multiple
                placeholder="选择水果类型"
                style="width: 100%"
              >
                <el-option label="苹果" value="apple" />
                <el-option label="香蕉" value="banana" />
                <el-option label="橘子" value="orange" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="成熟度">
              <el-select
                v-model="form.maturity_levels"
                multiple
                placeholder="选择成熟度"
                style="width: 100%"
              >
                <el-option label="未成熟" value="unripe" />
                <el-option label="成熟" value="ripe" />
                <el-option label="过熟" value="overripe" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <!-- 分析结果 -->
      <div v-if="summary" class="summary-result">
        <el-card class="result-card">
          <template #header>
            <span>分析摘要</span>
          </template>
          <p>{{ summary.data.summary }}</p>
        </el-card>
        
        <el-row :gutter="20" class="result-row">
          <el-col :span="12">
            <el-card class="result-card">
              <template #header>
                <span>关键洞察</span>
              </template>
              <el-list>
                <el-list-item v-for="(insight, index) in summary.data.key_insights" :key="index">
                  <span class="insight-item">{{ insight }}</span>
                </el-list-item>
              </el-list>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="result-card">
              <template #header>
                <span>建议</span>
              </template>
              <el-list>
                <el-list-item v-for="(recommendation, index) in summary.data.recommendations" :key="index">
                  <span class="recommendation-item">{{ recommendation }}</span>
                </el-list-item>
              </el-list>
            </el-card>
          </el-col>
        </el-row>
        
        <el-card class="result-card">
          <template #header>
            <span>统计数据</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="总检测次数">
              {{ summary.data.statistics.total_detections }}
            </el-descriptions-item>
            <el-descriptions-item label="总水果数量">
              {{ summary.data.statistics.total_fruits }}
            </el-descriptions-item>
            <el-descriptions-item label="最常见水果">
              {{ summary.data.statistics.most_common_fruit }}
            </el-descriptions-item>
            <el-descriptions-item label="最常见成熟度">
              {{ summary.data.statistics.most_common_maturity }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <div class="action-buttons">
          <el-button @click="exportSummary">导出报告</el-button>
          <el-button type="success" @click="shareSummary">分享报告</el-button>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-else class="empty-state">
        <el-empty description="点击生成分析报告" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { generateAiSummary, type AiSummaryRequest, type AiSummaryResponse } from '@/api/ai'

const form = ref<AiSummaryRequest>({})
const summary = ref<AiSummaryResponse | null>(null)
const loading = ref(false)

const generateSummary = async () => {
  loading.value = true
  try {
    summary.value = await generateAiSummary(form.value)
  } catch (error) {
    console.error('生成分析报告失败', error)
  } finally {
    loading.value = false
  }
}

const exportSummary = () => {
  // 导出功能实现
  console.log('导出报告')
}

const shareSummary = () => {
  // 分享功能实现
  console.log('分享报告')
}
</script>

<style scoped>
.ai-summary {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-form {
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.summary-result {
  margin-top: 20px;
}

.result-card {
  margin-bottom: 20px;
}

.result-row {
  margin-bottom: 20px;
}

.insight-item,
.recommendation-item {
  line-height: 1.6;
}

.action-buttons {
  margin-top: 30px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}
</style>