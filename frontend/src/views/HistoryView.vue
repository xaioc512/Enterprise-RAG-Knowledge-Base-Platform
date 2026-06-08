<template>
  <div class="hist-shell">
    <aside class="hist-sidebar">
      <div class="sb-brand">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 0L12 7L18 9L12 11L9 18L6 11L0 9L6 7Z" fill="var(--color-primary)"/></svg>
        <router-link to="/" class="sb-name-link">企业AI知识库</router-link>
      </div>
      <nav class="conv-list" v-if="conversations.length">
        <div v-for="conv in conversations" :key="conv.id" class="conv-item" :class="{ active: conv.id === activeId }" @click="loadConv(conv)">
          <span class="conv-title">{{ conv.title }}</span>
          <span class="conv-date">{{ fmtDate(conv.updated_at) }}</span>
        </div>
      </nav>
      <div class="conv-empty" v-else><p>暂无对话记录</p></div>
      <router-link to="/" class="sb-back">← 新对话</router-link>
    </aside>

    <main class="hist-main">
      <div v-if="!activeId" class="empty-state">
        <h1 class="empty-title">对话历史</h1>
        <p class="empty-desc">选择左侧对话查看详情</p>
      </div>

      <div v-else class="conv-view">
        <h1 class="view-title">{{ activeTitle }}</h1>
        <div v-for="(msg, i) in messages" :key="i" class="msg-block" :class="msg.role">
          <div class="msg-label">{{ msg.role === 'user' ? '用户' : 'AI 助手' }}</div>
          <div class="msg-text" v-html="renderMd(msg.content)"></div>
          <div v-if="msg.sources?.length" class="msg-src-list">
            <span v-for="(s, si) in msg.sources" :key="si" class="src-chip">{{ s.title }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'; import { marked } from 'marked'; import api from '../api'
const conversations = ref([]); const activeId = ref(null); const activeTitle = ref(''); const messages = ref([])
onMounted(async () => { try { conversations.value = (await api.get('/conversations/')).data.items } catch {} })
async function loadConv(conv) { activeId.value = conv.id; activeTitle.value = conv.title; try { messages.value = (await api.get(`/conversations/${conv.id}`)).data.messages || [] } catch {} }
function renderMd(t) { return marked.parse(t || '', { breaks: true }) }
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('zh-CN') : '' }
</script>

<style scoped>
.hist-shell { display: flex; height: 100vh; background: var(--color-canvas); }
.hist-sidebar { width: clamp(220px, 18vw, 300px); background: var(--color-surface-dark); display: flex; flex-direction: column; padding: clamp(12px, 1.5vw, 24px); flex-shrink: 0; }
.sb-brand { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-lg); }
.sb-name-link { color: var(--color-on-dark); font: var(--text-title-sm); }
.conv-list { flex: 1; overflow-y: auto; }
.conv-item { padding: var(--space-sm) var(--space-md); border-radius: var(--radius-sm); cursor: pointer; margin-bottom: 2px; color: var(--color-on-dark-soft); font: var(--text-body-sm); transition: all var(--transition-fast); }
.conv-item:hover, .conv-item.active { background: rgba(255,255,255,0.06); color: var(--color-on-dark); }
.conv-title { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.conv-date { font: var(--text-caption); color: var(--color-on-dark-soft); }
.conv-empty { flex: 1; display: flex; align-items: center; justify-content: center; color: var(--color-on-dark-soft); font: var(--text-body-sm); }
.sb-back { color: var(--color-on-dark-soft); font: var(--text-caption); margin-top: var(--space-lg); padding-top: var(--space-md); border-top: 1px solid rgba(255,255,255,0.06); }

.hist-main { flex: 1; padding: var(--space-xl); overflow-y: auto; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; }
.empty-title { font: var(--text-display-sm); color: var(--color-ink); margin-bottom: var(--space-sm); }
.empty-desc { color: var(--color-muted); font: var(--text-body-md); }

.conv-view { max-width: 780px; }
.view-title { font: var(--text-display-sm); letter-spacing: var(--tracking-display-sm); color: var(--color-ink); margin-bottom: var(--space-xl); padding-bottom: var(--space-lg); border-bottom: 1px solid var(--color-hairline); }

.msg-block { margin-bottom: var(--space-xl); padding-left: var(--space-md); border-left: 2px solid var(--color-hairline); }
.msg-block.user { border-left-color: var(--color-primary); }
.msg-label { font: var(--text-caption); color: var(--color-muted); margin-bottom: var(--space-sm); }
.msg-text { font: var(--text-body-md); color: var(--color-body); line-height: 1.7; }
.msg-text :deep(pre) { background: var(--color-surface-dark); padding: var(--space-md); border-radius: var(--radius-md); overflow-x: auto; }
.msg-text :deep(pre code) { color: var(--color-on-dark); background: none; }
.msg-src-list { margin-top: var(--space-sm); display: flex; flex-wrap: wrap; gap: 4px; }
.src-chip { font: var(--text-caption); padding: 2px 8px; background: var(--color-surface-card); color: var(--color-muted); border-radius: var(--radius-pill); border: 1px solid var(--color-hairline); }
</style>
