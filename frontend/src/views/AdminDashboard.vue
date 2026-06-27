<template>
  <div class="admin-shell">
    <aside class="admin-sidebar">
      <div class="sb-brand"><svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 0L12 7L18 9L12 11L9 18L6 11L0 9L6 7Z" fill="var(--color-primary)"/></svg><span class="sb-name">知识库管理</span></div>
      <nav class="sb-nav">
        <router-link to="/admin" class="sb-link active">概览</router-link>
        <router-link to="/admin/documents" class="sb-link">文档管理</router-link>
        <router-link to="/admin/categories" class="sb-link">分类管理</router-link>
        <router-link to="/admin/departments" class="sb-link">部门管理</router-link>
        <router-link to="/admin/users" class="sb-link">用户管理</router-link>
      </nav>
      <router-link to="/" class="sb-back">← 返回问答</router-link>
    </aside>
    <main class="admin-main">
      <h1 class="page-title">数据概览</h1>

      <!-- 核心指标 -->
      <div class="stat-cards">
        <div class="stat-card"><span class="stat-num">{{ overview.documents }}</span><span class="stat-label">文档总数</span><span class="stat-sub">今日 +{{ overview.today_documents }}</span></div>
        <div class="stat-card"><span class="stat-num">{{ overview.questions }}</span><span class="stat-label">总提问数</span><span class="stat-sub">今日 +{{ overview.today_questions }}</span></div>
        <div class="stat-card"><span class="stat-num">{{ overview.users }}</span><span class="stat-label">用户总数</span></div>
        <div class="stat-card"><span class="stat-num">{{ overview.conversations }}</span><span class="stat-label">对话总数</span></div>
      </div>

      <!-- 趋势图 + 反馈 -->
      <div class="charts-row">
        <div class="chart-card">
          <h4 class="chart-title">近7天提问趋势</h4>
          <v-chart :option="trendOption" style="height:260px" autoresize />
        </div>
        <div class="chart-card">
          <h4 class="chart-title">反馈统计</h4>
          <v-chart :option="feedbackOption" style="height:260px" autoresize />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import api from '../api'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent])

const overview = ref({ documents: 0, today_documents: 0, users: 0, questions: 0, today_questions: 0, conversations: 0 })
const trends = ref([])
const feedback = ref({ like: 0, dislike: 0 })

const trendOption = computed(() => ({
  grid: { top: 20, right: 20, bottom: 30, left: 40 },
  xAxis: { type: 'category', data: trends.value.map(t => t.date.slice(5)), axisLine: { lineStyle: { color: '#e6dfd8' } }, axisLabel: { color: '#8e8b82', fontSize: 11 } },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: '#ebe6df' } }, axisLabel: { color: '#8e8b82', fontSize: 11 } },
  series: [{ data: trends.value.map(t => t.count), type: 'line', smooth: true, lineStyle: { color: '#cc785c', width: 2 }, itemStyle: { color: '#cc785c' }, areaStyle: { color: 'rgba(204,120,92,0.08)' } }],
  tooltip: { trigger: 'axis' },
}))

const feedbackOption = computed(() => ({
  grid: { top: 20, right: 20, bottom: 30, left: 40 },
  xAxis: { type: 'category', data: ['👍 点赞', '👎 点踩'], axisLine: { lineStyle: { color: '#e6dfd8' } }, axisLabel: { color: '#8e8b82', fontSize: 12 } },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: '#ebe6df' } }, axisLabel: { color: '#8e8b82', fontSize: 11 } },
  series: [{ data: [feedback.value.like, feedback.value.dislike], type: 'bar', barWidth: '50%', itemStyle: { color: '#5db872', borderRadius: [4,4,0,0] } }],
}))

onMounted(async () => {
  try { overview.value = (await api.get('/stats/overview')).data } catch {}
  try { trends.value = (await api.get('/stats/trends?days=7')).data } catch {}
  try { feedback.value = (await api.get('/stats/feedback')).data } catch {}
})
</script>

<style scoped>
.admin-shell { display: flex; min-height: 100vh; background: var(--color-canvas); }
.admin-sidebar { width: clamp(200px, 16vw, 280px); background: var(--color-surface-dark); display: flex; flex-direction: column; padding: clamp(12px, 1.5vw, 24px); flex-shrink: 0; }
.sb-brand { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-xl); }
.sb-name { color: var(--color-on-dark); font: var(--text-title-sm); }
.sb-nav { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.sb-link { padding: var(--space-sm) var(--space-md); border-radius: var(--radius-sm); color: var(--color-on-dark-soft); font: var(--text-body-sm); transition: all var(--transition-fast); }
.sb-link:hover, .sb-link.active { background: rgba(255,255,255,0.06); color: var(--color-on-dark); }
.sb-back { color: var(--color-on-dark-soft); font: var(--text-caption); margin-top: var(--space-lg); padding-top: var(--space-md); border-top: 1px solid rgba(255,255,255,0.06); }
.admin-main { flex: 1; padding: clamp(20px, 2.5vw, 40px); overflow-y: auto; }
.page-title { font: var(--text-display-sm); letter-spacing: var(--tracking-display-sm); color: var(--color-ink); margin-bottom: clamp(20px, 2vw, 32px); }

.stat-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--space-md); margin-bottom: var(--space-xl); }
.stat-card { padding: var(--space-xl); background: var(--color-canvas); border: 1px solid var(--color-hairline); border-radius: var(--radius-lg); text-align: center; }
.stat-num { display: block; font: var(--text-display-sm); font-size: var(--fs-display-lg); color: var(--color-ink); }
.stat-label { font: var(--text-body-sm); color: var(--color-muted); display: block; margin-top: var(--space-xs); }
.stat-sub { font: var(--text-caption); color: var(--color-success); margin-top: 2px; display: block; }

.charts-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: var(--space-md); }
.chart-card { padding: var(--space-xl); background: var(--color-canvas); border: 1px solid var(--color-hairline); border-radius: var(--radius-lg); }
.chart-title { font: var(--text-title-sm); color: var(--color-ink); margin-bottom: var(--space-md); }
</style>
