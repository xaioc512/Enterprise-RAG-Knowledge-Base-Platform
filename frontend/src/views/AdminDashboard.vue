<template>
  <div class="admin-shell">
    <aside class="admin-sidebar">
      <div class="sb-brand"><svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 0L12 7L18 9L12 11L9 18L6 11L0 9L6 7Z" fill="var(--color-primary)"/></svg><span class="sb-name">知识库管理</span></div>
      <nav class="sb-nav">
        <router-link to="/admin" class="sb-link active">概览</router-link>
        <router-link to="/admin/documents" class="sb-link">文档管理</router-link>
        <router-link to="/admin/categories" class="sb-link">分类管理</router-link>
        <router-link to="/admin/users" class="sb-link">用户管理</router-link>
      </nav>
      <router-link to="/" class="sb-back">← 返回问答</router-link>
    </aside>
    <main class="admin-main">
      <h1 class="page-title">管理概览</h1>
      <div class="stat-grid">
        <div class="stat-card"><span class="stat-num">{{ stats.documents }}</span><span class="stat-label">文档总数</span></div>
        <div class="stat-card"><span class="stat-num">{{ stats.conversations }}</span><span class="stat-label">对话总数</span></div>
        <div class="stat-card"><span class="stat-num">{{ stats.users }}</span><span class="stat-label">用户总数</span></div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'; import api from '../api'
const stats = ref({ documents: 0, conversations: 0, users: 0 })
onMounted(async () => {
  try { const [d, u] = await Promise.all([api.get('/documents/'), api.get('/users/')]); stats.value.documents = d.data.total; stats.value.users = u.data.total } catch {}
  try { stats.value.conversations = (await api.get('/conversations/')).data.total } catch {}
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
.admin-main { flex: 1; padding: var(--space-xl); }
.page-title { font: var(--text-display-sm); letter-spacing: var(--tracking-display-sm); color: var(--color-ink); margin-bottom: var(--space-xl); }
.stat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--space-md); }
.stat-card { padding: var(--space-xl); background: var(--color-surface-card); border-radius: var(--card-radius); text-align: center; }
.stat-num { display: block; font: var(--text-display-sm); color: var(--color-ink); }
.stat-label { font: var(--text-body-sm); color: var(--color-muted); margin-top: var(--space-xs); }
</style>
