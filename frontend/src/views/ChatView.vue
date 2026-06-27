<template>
  <div class="chat-app">
    <!-- 深色侧边栏 -->
    <aside class="sidebar-dark">
      <div class="sidebar-brand">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <path d="M9 0L12 7L18 9L12 11L9 18L6 11L0 9L6 7Z" fill="var(--color-primary)"/>
        </svg>
        <h4 class="brand-name">企业AI知识库</h4>
      </div>

      <button class="new-chat-btn" @click="newConversation">
        <span>+ 新对话</span>
      </button>

      <nav class="conv-list" v-if="conversations.length">
        <div
          v-for="conv in sortedConversations"
          :key="conv.id"
          class="conv-item"
          :class="{ active: conv.id === currentConvId, pinned: pinnedIds.includes(conv.id) }"
          @click="menuOpenId === conv.id ? null : selectConversation(conv)"
        >
          <!-- 删除确认 -->
          <template v-if="deletingConvId === conv.id">
            <span class="confirm-inline">确定删除？</span>
            <button class="btn-confirm-inline" @click.stop="deleteConversation(conv.id); deletingConvId = null">确定</button>
            <button class="btn-cancel-inline" @click.stop="deletingConvId = null">取消</button>
          </template>

          <!-- 重命名 -->
          <template v-else-if="renamingId === conv.id">
            <input
              v-model="renameText"
              class="rename-input"
              @keydown.enter="doRename(conv.id)"
              @keydown.escape="renamingId = null"
              @blur="doRename(conv.id)"
              ref="renameInputRef"
            />
          </template>

          <!-- 正常显示 -->
          <template v-else>
            <span class="conv-title">{{ conv.title }}</span>
            <button class="conv-menu-btn" @click.stop="toggleMenu(conv.id, $event)" title="更多操作">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><circle cx="3" cy="8" r="1.5"/><circle cx="8" cy="8" r="1.5"/><circle cx="13" cy="8" r="1.5"/></svg>
            </button>

          </template>
        </div>
      </nav>
      <div class="conv-empty" v-else>
        <p>暂无对话记录</p>
      </div>

      <div class="sidebar-actions">
        <router-link v-if="authStore.isAdmin" to="/admin/documents" class="admin-link">管理后台</router-link>
        <span class="user-label">{{ authStore.user?.username }}</span>
        <button class="logout-btn" @click="handleLogout">退出</button>
      </div>
    </aside>

    <!-- 主聊天区 -->
    <main class="chat-main">
      <!-- 顶部条 -->
      <div class="chat-topbar">
        <span class="conv-label" v-if="currentConvId && currentConvTitle">{{ currentConvTitle }}</span>
        <span class="conv-label muted" v-else>AI 知识库助手</span>
        <div class="mode-toggle">
          <button :class="['mode-btn', { active: chatMode === 'rag' }]" @click="chatMode = 'rag'">RAG</button>
          <button :class="['mode-btn', { active: chatMode === 'agent' }]" @click="chatMode = 'agent'">Agent</button>
        </div>
      </div>

      <!-- 消息区 -->
      <div class="messages-area" ref="msgArea">
        <!-- 欢迎 -->
        <div v-if="!currentConvId && !streaming && messages.length === 0" class="welcome-card" :style="{ animation: 'fade-in-up 0.6s ease both' }">
          <h1 class="welcome-title">向你的企业<br/>知识库提问</h1>
          <p class="welcome-desc">
            制度规范、工艺流程、技术文档 —<br/>
            AI 精准回答，来源可溯源。
          </p>
          <div class="welcome-hints">
            <span class="hint-chip" v-for="q in sampleQuestions" :key="q" @click="inputText = q; sendMessage()">「{{ q }}」</span>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="msg-row"
          :class="msg.role"
          :style="{ animation: 'fade-in-up 0.3s ease both', animationDelay: `${i * 0.02}s` }"
        >
          <div class="msg-avatar">
            <span v-if="msg.role === 'user'">{{ authStore.user?.username?.[0]?.toUpperCase() || 'U' }}</span>
            <span v-else>AI</span>
          </div>
          <div class="msg-body">
            <div class="msg-content" v-html="renderMd(msg.content)"></div>
            <!-- 来源 -->
            <div v-if="msg.sources?.length" class="msg-sources">
              <span class="src-label">参考来源</span>
              <span v-for="(src, si) in msg.sources" :key="si" class="src-tag">{{ src.title }}</span>
            </div>
            <!-- 反馈 -->
            <div v-if="msg.role === 'assistant' && msg.id" class="msg-feedback">
              <button class="fb-btn" :class="{ on: msg.feedback === 'like' }" @click="submitFeedback(msg, 'like')">
                <svg width="15" height="15" viewBox="0 0 15 15" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 6v6M7.5 3l-1.5 7h4.5a1.5 1.5 0 011.5 1.5V12l-2 4H4V6l3.5-3z"/></svg>
              </button>
              <button class="fb-btn" :class="{ on: msg.feedback === 'dislike' }" @click="submitFeedback(msg, 'dislike')">
                <svg width="15" height="15" viewBox="0 0 15 15" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 9V3m3.5 12l-1.5-7h4.5a1.5 1.5 0 001.5-1.5V3l-2-4H4v6l3.5 3z"/></svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Agent 思考步骤 -->
        <div v-if="streaming && thinkingSteps.length" class="thinking-bar" :style="{ animation: 'fade-in-up 0.3s ease both' }">
          <div class="thinking-header">
            <span class="thinking-dot"></span>
            <span>AI Agent 思考中</span>
          </div>
          <div class="thinking-steps">
            <div v-for="(step, i) in thinkingSteps" :key="i" class="think-step" :style="{ animation: `fade-in-up 0.25s ease both`, animationDelay: `${i * 0.1}s` }">
              <span class="step-check">{{ i < thinkingSteps.length - 1 ? '✓' : '·' }}</span>
              {{ step }}
            </div>
          </div>
        </div>

        <!-- 流式输出中 -->
        <div v-if="streaming" class="msg-row assistant">
          <div class="msg-avatar"><span>AI</span></div>
          <div class="msg-body">
            <div class="msg-content" v-html="renderMd(streamText)"></div>
            <span class="cursor-blink">|</span>
            <div v-if="streamSources.length" class="msg-sources">
              <span class="src-label">参考来源</span>
              <span v-for="(src, si) in streamSources" :key="si" class="src-tag">{{ src.title }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="input-bar">
        <div class="input-wrap">
          <textarea
            v-model="inputText"
            placeholder="输入问题，基于知识库获取答案..."
            :disabled="streaming"
            class="chat-textarea"
            rows="1"
            @keydown.enter.exact.prevent="sendMessage()"
            @input="autoResize"
            ref="textareaRef"
          ></textarea>
          <button class="send-icon-btn" :disabled="!inputText.trim() || streaming" @click="sendMessage()">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M2 9l14-7L9 16l-2-7H2z"/>
            </svg>
          </button>
        </div>
      </div>
    </main>

    <!-- 全局下拉菜单 — 渲染在最外层，不受 overflow 裁剪 -->
    <Teleport to="body">
      <div
        v-if="menuOpenId"
        class="conv-dropdown"
        :style="{ top: dropdownY + 'px', left: dropdownX + 'px' }"
        @click.stop
      >
        <button class="dropdown-item" @click="togglePin(menuOpenId); menuOpenId = null">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9.5 1.5L3.5 5.5v3l-2 2.5h11l-2-2.5v-3L4.5 1.5"/></svg>
          {{ pinnedIds.includes(menuOpenId) ? '取消置顶' : '置顶' }}
        </button>
        <button class="dropdown-item" @click="toggleFav(menuOpenId); menuOpenId = null">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M7 1l2 4 4 .5-3 3 .5 4.5L7 11l-3.5 2 .5-4.5-3-3 4-.5z"/></svg>
          {{ favIds.includes(menuOpenId) ? '已收藏' : '收藏' }}
        </button>
        <button class="dropdown-item" @click="startRenameById(menuOpenId); menuOpenId = null">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 1.5l2.5 2.5M3 10.5l7-7M2 12l1-4 3 3z"/></svg>
          重命名
        </button>
        <div class="dropdown-divider"></div>
        <button class="dropdown-item danger" @click="deletingConvId = menuOpenId; menuOpenId = null">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 3h10M4.5 3V2h5v1M3 3l1 9.5h6L11 3"/></svg>
          删除
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { marked } from 'marked'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import ConfirmPop from '../components/ConfirmPop.vue'

const router = useRouter()
const authStore = useAuthStore()

const conversations = ref([])
const deletingConvId = ref(null)
const currentConvId = ref(null)
const menuOpenId = ref(null)
const renamingId = ref(null)
const renameText = ref('')
const renameInputRef = ref(null)
const pinnedIds = ref(JSON.parse(localStorage.getItem('pinnedConvs') || '[]'))
const favIds = ref(JSON.parse(localStorage.getItem('favConvs') || '[]'))
const currentConvTitle = ref('')
const messages = ref([])
const inputText = ref('')
const streaming = ref(false)
const streamText = ref('')
const streamSources = ref([])
const chatMode = ref('rag')
const thinkingSteps = ref([])
const msgArea = ref(null)
const textareaRef = ref(null)

const sampleQuestions = ref([])

onMounted(() => { fetchConversations(); fetchSuggestions(); document.addEventListener('click', onGlobalClick) })
onUnmounted(() => document.removeEventListener('click', onGlobalClick))
function onGlobalClick() { menuOpenId.value = null }

async function fetchSuggestions() {
  try { sampleQuestions.value = (await api.get('/suggestions/')).data } catch {
    sampleQuestions.value = ['考勤迟到有什么处罚？', '加班补偿标准是什么？', '请假流程是怎样的？']
  }
}
watch(() => messages.value.length, async () => { await nextTick(); scrollToBottom() })

async function fetchConversations() {
  try { conversations.value = (await api.get('/conversations/')).data.items } catch {}
}

function newConversation() {
  currentConvId.value = null
  currentConvTitle.value = ''
  messages.value = []
  streamText.value = ''
  streamSources.value = []
}

async function selectConversation(conv) {
  currentConvId.value = conv.id
  currentConvTitle.value = conv.title
  messages.value = []
  try {
    const res = await api.get(`/conversations/${conv.id}`)
    messages.value = (res.data.messages || []).map(m => ({ ...m, feedback: null }))
    await nextTick(); scrollToBottom()
  } catch {}
}

async function deleteConversation(id, event) {
  event?.stopPropagation()
  try {
    await api.delete(`/conversations/${id}`)
    if (currentConvId.value === id) newConversation()
    fetchConversations()
  } catch {}
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || streaming.value) return
  inputText.value = ''

  messages.value.push({ role: 'user', content: text })
  if (!currentConvId.value) { currentConvTitle.value = text.slice(0, 30) }

  streamText.value = ''; streamSources.value = []; thinkingSteps.value = []; streaming.value = true

  try {
    const response = await fetch('/api/chat/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${authStore.token}` },
      body: JSON.stringify({ conversation_id: currentConvId.value, message: text, mode: chatMode.value }),
    })

    const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n'); buffer = lines.pop() || ''
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        try {
          const data = JSON.parse(line.slice(6))
          if (data.type === 'thinking') { thinkingSteps.value.push(data.step); await nextTick(); scrollToBottom() }
          else if (data.type === 'sources') { streamSources.value = data.sources }
          else if (data.type === 'token') { streamText.value += data.content; await nextTick(); scrollToBottom() }
          else if (data.type === 'done') {
            currentConvId.value = data.conversation_id
            messages.value.push({ id: data.message_id, role: 'assistant', content: streamText.value, sources: streamSources.value, feedback: null })
            streamText.value = ''; streamSources.value = []
            fetchConversations()
          } else if (data.type === 'error') {
            messages.value.push({ role: 'assistant', content: `❌ ${data.message}` })
          }
        } catch {}
      }
    }
  } catch {
    messages.value.push({ role: 'assistant', content: '❌ 网络请求失败。' })
  } finally {
    streaming.value = false; await nextTick(); scrollToBottom()
  }
}

async function submitFeedback(msg, rating) {
  if (!msg.id) return
  try { await api.post('/feedback/', { message_id: msg.id, rating }); msg.feedback = rating } catch {}
}

function scrollToBottom() {
  if (msgArea.value) msgArea.value.scrollTop = msgArea.value.scrollHeight
}

function autoResize() {
  const el = textareaRef.value
  if (el) { el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 160) + 'px' }
}

function renderMd(text) { return marked.parse(text || '', { breaks: true }) }

function handleLogout() { authStore.logout(); router.push('/login') }

const dropdownX = ref(0)
const dropdownY = ref(0)

function toggleMenu(id, event) {
  if (menuOpenId.value === id) { menuOpenId.value = null; return }
  const rect = event.currentTarget.getBoundingClientRect()
  dropdownX.value = rect.left + 75  // 菜单在按钮右侧
  dropdownY.value = rect.bottom + 4
  menuOpenId.value = id
}
function togglePin(id) {
  const idx = pinnedIds.value.indexOf(id)
  if (idx > -1) pinnedIds.value.splice(idx, 1)
  else pinnedIds.value.unshift(id)
  localStorage.setItem('pinnedConvs', JSON.stringify(pinnedIds.value))
}
function toggleFav(id) {
  const idx = favIds.value.indexOf(id)
  if (idx > -1) favIds.value.splice(idx, 1)
  else favIds.value.push(id)
  localStorage.setItem('favConvs', JSON.stringify(favIds.value))
}
function startRename(conv) { renamingId.value = conv.id; renameText.value = conv.title; setTimeout(() => renameInputRef.value?.focus(), 50) }
function startRenameById(id) { const c = conversations.value.find(x => x.id === id); if (c) startRename(c) }
async function doRename(id) {
  const title = renameText.value.trim()
  renamingId.value = null
  if (!title) return
  try { await api.put(`/conversations/${id}/title`, null, { params: { title } }); fetchConversations() } catch {}
}

// 置顶排序
const sortedConversations = computed(() => {
  const convs = [...conversations.value]
  convs.sort((a, b) => {
    const aPin = pinnedIds.value.includes(a.id) ? 1 : 0
    const bPin = pinnedIds.value.includes(b.id) ? 1 : 0
    return bPin - aPin
  })
  return convs
})
</script>

<style scoped>
.chat-app { display: flex; height: 100vh; background: var(--color-canvas); }

/* --- Sidebar (Dark Navy) --- */
.sidebar-dark {
  width: clamp(220px, 18vw, 300px); background: var(--color-surface-dark); display: flex;
  flex-direction: column; padding: clamp(16px, 1.5vw, 28px); flex-shrink: 0;
}
.sidebar-brand { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-lg); }
.brand-name { color: var(--color-on-dark); font: var(--text-title-sm); }

.new-chat-btn {
  width: 100%; padding: var(--space-sm) 0; margin-bottom: var(--space-lg);
  background: var(--color-surface-dark-elevated); color: var(--color-on-dark);
  border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius-md);
  font: var(--text-button); cursor: pointer; transition: background var(--transition-fast);
}
.new-chat-btn:hover { background: rgba(255,255,255,0.08); }

.conv-list { flex: 1; overflow-y: auto; }
.conv-item {
  display: flex; align-items: center; padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-sm); cursor: pointer; margin-bottom: 2px;
  color: var(--color-on-dark-soft); font: var(--text-body-sm); transition: all var(--transition-fast);
  position: relative;
}
.conv-item:hover, .conv-item.active { background: rgba(255,255,255,0.06); color: var(--color-on-dark); }
.conv-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.conv-menu-btn {
  background: none; border: none; color: var(--color-on-dark-soft);
  cursor: pointer; padding: 4px; border-radius: var(--radius-xs);
  flex-shrink: 0; display: flex; opacity: 0.5; transition: opacity var(--transition-fast);
}
.conv-menu-btn:hover { opacity: 1; background: rgba(255,255,255,0.08); color: var(--color-on-dark); }

/* 下拉菜单 — fixed 定位突破 sidebar overflow */
.conv-dropdown {
  position: fixed; z-index: 100;
  min-width: 160px; background: #fefbf2;
  border: 1px solid #d4cec2; border-radius: var(--radius-md);
  box-shadow: 0 4px 16px rgba(20,20,19,0.10); padding: var(--space-xxs);
  display: flex; flex-direction: column;
}
.dropdown-item {
  display: flex; align-items: center; gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md); border: none; background: transparent;
  color: var(--color-body); font: var(--text-body-sm); cursor: pointer;
  border-radius: var(--radius-sm); transition: all var(--transition-fast);
  text-align: left; white-space: nowrap;
}
.dropdown-item:hover { background: var(--color-surface-cream-strong); color: var(--color-ink); }
.dropdown-item.danger:hover { background: rgba(198,69,69,0.08); color: var(--color-error); }
.dropdown-divider { height: 1px; background: var(--color-hairline); margin: var(--space-xxs) 0; }

/* 置顶标记 */
.conv-item.pinned { background: rgba(255,255,255,0.03); }
.conv-item.pinned::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 2px; background: var(--color-primary); border-radius: 0 2px 2px 0; }

/* 重命名输入 */
.rename-input {
  flex: 1; background: rgba(255,255,255,0.08); border: 1px solid var(--color-primary);
  border-radius: var(--radius-sm); color: var(--color-on-dark);
  font: var(--text-body-sm); padding: 4px 8px; outline: none; min-width: 0;
}

/* 删除确认 */
.confirm-inline { font: var(--text-caption); color: var(--color-on-dark); white-space: nowrap; flex: 1; overflow: hidden; text-overflow: ellipsis; }
.btn-confirm-inline { height: 26px; padding: 0 10px; font: var(--text-caption); font-weight: 500; background: var(--color-primary); color: var(--color-on-primary); border: none; border-radius: var(--radius-sm); cursor: pointer; flex-shrink: 0; }
.btn-confirm-inline:hover { background: var(--color-primary-active); }
.btn-cancel-inline { height: 26px; padding: 0 8px; font: var(--text-caption); background: transparent; color: var(--color-on-dark-soft); border: 1px solid rgba(255,255,255,0.12); border-radius: var(--radius-sm); cursor: pointer; flex-shrink: 0; }
.btn-cancel-inline:hover { border-color: rgba(255,255,255,0.25); color: var(--color-on-dark); }

.conv-empty { flex: 1; display: flex; align-items: center; justify-content: center; color: var(--color-on-dark-soft); font: var(--text-body-sm); }

.sidebar-actions {
  margin-top: auto; padding-top: var(--space-md);
  border-top: 1px solid rgba(255,255,255,0.06);
  display: flex; align-items: center; gap: var(--space-sm); flex-wrap: wrap;
}
.admin-link { color: var(--color-primary); font: var(--text-caption); }
.user-label { color: var(--color-on-dark-soft); font: var(--text-caption); }
.logout-btn { background: none; border: none; color: var(--color-on-dark-soft); font: var(--text-caption); cursor: pointer; }

/* --- Main Chat Area --- */
.chat-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.chat-topbar {
  height: clamp(48px, 4vh, 62px); display: flex; align-items: center;
  padding: 0 clamp(16px, 2.5vw, 40px);
  border-bottom: 1px solid var(--color-hairline); background: var(--color-canvas);
}
.conv-label { font: var(--text-title-sm); color: var(--color-ink); }
.conv-label.muted { color: var(--color-muted); }
.mode-toggle {
  margin-left: auto; display: flex; gap: 2px;
  background: var(--color-surface-card); border-radius: var(--radius-md); padding: 3px;
}
.mode-btn {
  padding: 5px 14px; border: none; background: transparent;
  font: var(--text-caption); font-weight: 500; color: var(--color-muted);
  border-radius: var(--radius-sm); cursor: pointer; transition: all var(--transition-fast);
}
.mode-btn.active { background: var(--color-canvas); color: var(--color-ink); box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.mode-btn:hover:not(.active) { color: var(--color-body); }

/* Thinking indicator */
.thinking-bar {
  max-width: min(88%, 900px); margin: 0 auto var(--space-lg); padding: var(--space-md) var(--space-lg);
  background: var(--color-surface-card); border-radius: var(--radius-lg); border: 1px solid var(--color-hairline);
}
.thinking-header { display: flex; align-items: center; gap: var(--space-sm); font: var(--text-caption); font-weight: 500; color: var(--color-ink); margin-bottom: var(--space-sm); }
.thinking-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--color-accent-amber); animation: pulse 1.2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
.thinking-steps { display: flex; flex-direction: column; gap: 2px; }
.think-step { font: var(--text-caption); color: var(--color-muted); display: flex; align-items: center; gap: var(--space-xs); }
.step-check { color: var(--color-success); font-size: 11px; width: 14px; flex-shrink: 0; }

.messages-area {
  flex: 1; overflow-y: auto;
  padding: clamp(16px, 2.5vw, 48px) clamp(16px, 3vw, 56px) 0;
  scroll-behavior: smooth;
}

/* Welcome */
.welcome-card {
  max-width: min(90%, 700px); margin: 8vh auto 0; text-align: center;
  padding: clamp(24px, 4vw, 64px) clamp(16px, 3vw, 48px);
}
.welcome-title {
  font: var(--text-display-lg); letter-spacing: var(--tracking-display-lg);
  color: var(--color-ink); margin-bottom: var(--space-lg);
}
.welcome-desc { font: var(--text-body-md); color: var(--color-body); margin-bottom: var(--space-xl); }
.welcome-hints { display: flex; flex-wrap: wrap; justify-content: center; gap: var(--space-sm); }
.hint-chip {
  padding: var(--space-xs) var(--space-md); background: var(--color-surface-card);
  border-radius: var(--radius-pill); font: var(--text-body-sm); color: var(--color-body);
  cursor: pointer; transition: all var(--transition-fast);
  border: 1px solid var(--color-hairline);
}
.hint-chip:hover { background: var(--color-surface-cream-strong); color: var(--color-ink); }

/* Messages */
.msg-row { display: flex; gap: var(--space-md); margin-bottom: var(--space-lg); max-width: min(88%, 900px); }
.msg-row.user { margin-left: auto; flex-direction: row-reverse; }
.msg-avatar {
  width: 34px; height: 34px; border-radius: var(--radius-sm); flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font: var(--text-caption); font-weight: 600;
}
.msg-row.user .msg-avatar { background: var(--color-primary); color: var(--color-on-primary); }
.msg-row.assistant .msg-avatar { background: var(--color-surface-card); color: var(--color-ink); }

.msg-body { flex: 1; min-width: 0; }
.msg-content { font: var(--text-body-md); color: var(--color-body); line-height: 1.7; }
.msg-content :deep(p) { margin-bottom: var(--space-sm); }
.msg-content :deep(code) { font: var(--text-code); background: var(--color-surface-card); padding: 2px 6px; border-radius: var(--radius-xs); color: var(--color-ink); }
.msg-content :deep(pre) { background: var(--color-surface-dark); padding: var(--space-md); border-radius: var(--radius-md); overflow-x: auto; margin: var(--space-sm) 0; }
.msg-content :deep(pre code) { background: none; padding: 0; color: var(--color-on-dark); }

.msg-row.user .msg-content {
  background: var(--color-surface-card); padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-lg) var(--radius-xs) var(--radius-lg) var(--radius-lg);
}

.msg-sources { margin-top: var(--space-sm); display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-xxs); }
.src-label { font: var(--text-caption); color: var(--color-muted-soft); margin-right: var(--space-xxs); }
.src-tag {
  font: var(--text-caption); padding: 2px 8px; background: var(--color-surface-card);
  color: var(--color-muted); border-radius: var(--radius-pill); border: 1px solid var(--color-hairline);
}

.msg-feedback { margin-top: var(--space-xs); display: flex; gap: 2px; opacity: 0; transition: opacity var(--transition-fast); }
.msg-row:hover .msg-feedback { opacity: 1; }
.fb-btn {
  background: none; border: none; padding: 4px; cursor: pointer;
  color: var(--color-muted-soft); border-radius: var(--radius-sm); transition: all var(--transition-fast);
}
.fb-btn:hover { color: var(--color-body); background: var(--color-surface-card); }
.fb-btn.on { color: var(--color-primary); }

.cursor-blink { color: var(--color-primary); font-weight: 700; animation: blink 1s step-end infinite; }
@keyframes blink { 50% { opacity: 0; } }

/* Input Bar — 全宽底部输入栏 */
.input-bar {
  width: 100%;
  padding: clamp(12px, 1.5vw, 20px) clamp(16px, 3vw, 48px) clamp(16px, 2.5vw, 36px);
  border-top: 1px solid var(--color-hairline);
  background: var(--color-canvas);
}
.input-wrap {
  display: flex; align-items: flex-end; gap: var(--space-sm);
  background: var(--color-canvas); border: 1px solid var(--color-hairline);
  border-radius: var(--radius-lg);
  padding: clamp(6px, 0.8vw, 14px) clamp(6px, 0.8vw, 14px) clamp(6px, 0.8vw, 14px) clamp(10px, 1.2vw, 20px);
  transition: border-color var(--transition-fast);
  width: 100%;
}
.input-wrap:focus-within { border-color: var(--color-primary); box-shadow: 0 0 0 3px rgba(204,120,92,0.12); }
.chat-textarea {
  flex: 1; border: none; outline: none; background: transparent; resize: none;
  font: var(--text-body-md); color: var(--color-ink); padding: var(--space-xxs) 0;
}
.chat-textarea::placeholder { color: var(--color-muted-soft); }
.send-icon-btn {
  width: 38px; height: 38px; border-radius: var(--radius-md); border: none;
  background: var(--color-primary); color: var(--color-on-primary);
  display: flex; align-items: center; justify-content: center; cursor: pointer;
  flex-shrink: 0; transition: all var(--transition-fast);
}
.send-icon-btn:hover:not(:disabled) { background: var(--color-primary-active); }
.send-icon-btn:disabled { background: var(--color-primary-disabled); color: var(--color-muted); cursor: not-allowed; }

@media (max-width: 768px) {
  .sidebar-dark { display: none; }
  .welcome-title { font-size: 36px; }
}
</style>
