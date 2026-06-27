<template>
  <div class="admin-shell">
    <aside class="admin-sidebar">
      <div class="sb-brand"><svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 0L12 7L18 9L12 11L9 18L6 11L0 9L6 7Z" fill="var(--color-primary)"/></svg><span class="sb-name">知识库管理</span></div>
      <nav class="sb-nav">
        <router-link to="/admin/documents" class="sb-link">文档管理</router-link>
        <router-link to="/admin/categories" class="sb-link active">分类管理</router-link>
        <router-link to="/admin/departments" class="sb-link">部门管理</router-link>
        <router-link to="/admin/users" class="sb-link">用户管理</router-link>
      </nav>
      <router-link to="/" class="sb-back">← 返回问答</router-link>
    </aside>

    <main class="admin-main">
      <div class="page-head">
        <h1 class="page-title">知识分类</h1>
        <button class="btn-primary" @click="openCreate">新建分类</button>
      </div>

      <div class="card-grid">
        <div v-for="cat in categories" :key="cat.id" class="cat-card" :style="{ animation: 'fade-in-up 0.4s ease both', animationDelay: `${cat.sort_order * 0.05}s` }">
          <h4 class="cat-name">{{ cat.name }}</h4>
          <p class="cat-desc" v-if="cat.description">{{ cat.description }}</p>
          <button class="action-link danger" @click="handleDelete(cat.id)">删除</button>
        </div>
        <div v-if="!categories.length" class="empty-hint">暂无分类</div>
      </div>
    </main>

    <!-- 新建分类 — 自定义居中模态框 -->
    <Teleport to="body">
      <transition name="modal-fade">
        <div v-if="showCreate" class="modal-overlay" @click.self="closeCreate">
          <div class="modal-panel">
            <div class="modal-topbar">
              <span class="modal-title">新建分类</span>
              <button class="modal-close" @click="closeCreate">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M5 5l10 10M15 5l-10 10"/>
                </svg>
              </button>
            </div>

            <div class="modal-body">
              <div class="field-group">
                <label class="field-label">分类名称</label>
                <div class="input-row">
                  <input
                    ref="nameInputRef"
                    v-model="newName"
                    type="text"
                    placeholder="输入分类名称"
                    class="native-input"
                    @keydown.enter="handleCreate"
                  />
                </div>
              </div>

              <div class="field-group">
                <label class="field-label">描述（可选）</label>
                <div class="input-row">
                  <input
                    v-model="newDesc"
                    type="text"
                    placeholder="简要描述该分类的内容范围"
                    class="native-input"
                    @keydown.enter="handleCreate"
                  />
                </div>
              </div>

              <button class="btn-primary full" @click="handleCreate">确认创建</button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const categories = ref([])
const showCreate = ref(false)
const newName = ref('')
const newDesc = ref('')
const nameInputRef = ref(null)

onMounted(async () => { try { categories.value = (await api.get('/categories/')).data } catch {} })

function openCreate() {
  showCreate.value = true
  newName.value = ''
  newDesc.value = ''
  nextTick(() => nameInputRef.value?.focus())
}

function closeCreate() {
  showCreate.value = false
}

async function handleCreate() {
  if (!newName.value.trim()) return
  try {
    await api.post('/categories/', null, { params: { name: newName.value, description: newDesc.value } })
    ElMessage.success('创建成功')
    closeCreate()
    categories.value = (await api.get('/categories/')).data
  } catch (err) { ElMessage.error(err.response?.data?.detail || '创建失败') }
}

async function handleDelete(id) {
  try { await api.delete(`/categories/${id}`); ElMessage.success('已删除'); categories.value = (await api.get('/categories/')).data } catch { ElMessage.error('删除失败') }
}

// ESC 关闭
function onKeydown(e) { if (e.key === 'Escape' && showCreate.value) closeCreate() }
watch(showCreate, (v) => {
  if (v) document.addEventListener('keydown', onKeydown)
  else document.removeEventListener('keydown', onKeydown)
})
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
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

.admin-main { flex: 1; padding: var(--space-xl); overflow-y: auto; }
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-xl); }
.page-title { font: var(--text-display-sm); letter-spacing: var(--tracking-display-sm); }

.btn-primary { display: inline-flex; align-items: center; gap: var(--space-xs); padding: var(--btn-padding); height: var(--btn-height); background: var(--color-primary); color: var(--color-on-primary); border: none; border-radius: var(--btn-radius); font: var(--text-button); cursor: pointer; }
.btn-primary:hover { background: var(--color-primary-active); }
.btn-primary.full { width: 100%; justify-content: center; }

.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--space-md); }
.cat-card { padding: var(--space-xl); background: var(--color-surface-card); border-radius: var(--card-radius); }
.cat-card:hover { box-shadow: var(--shadow-hover); }
.cat-name { font: var(--text-title-md); color: var(--color-ink); margin-bottom: var(--space-sm); }
.cat-desc { font: var(--text-body-sm); color: var(--color-muted); margin-bottom: var(--space-md); }
.action-link { background: none; border: none; color: var(--color-primary); font: var(--text-caption); cursor: pointer; }
.action-link:hover { color: var(--color-primary-active); }
.action-link.danger { color: var(--color-muted); }
.action-link.danger:hover { color: var(--color-error); }
.empty-hint { grid-column: 1/-1; text-align: center; padding: var(--space-section); color: var(--color-muted); font: var(--text-body-md); }

/* --- 模态框 --- */
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  display: flex; align-items: center; justify-content: center;
  padding: clamp(24px, 4vw, 64px);
  background: rgba(20, 20, 19, 0.45);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.modal-fade-enter-active { transition: opacity 0.25s ease; }
.modal-fade-leave-active { transition: opacity 0.2s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-active .modal-panel { animation: modal-in 0.35s cubic-bezier(0.22, 0.61, 0.36, 1) both; }
.modal-fade-leave-active .modal-panel { animation: modal-out 0.2s ease both; }

@keyframes modal-in {
  from { opacity: 0; transform: translateY(24px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes modal-out {
  to { opacity: 0; transform: translateY(12px) scale(0.98); }
}

.modal-panel {
  width: min(92vw, 440px);
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-xl);
  box-shadow: 0 24px 80px rgba(20, 20, 19, 0.18);
  overflow: hidden;
}
.modal-topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--space-md) var(--space-xl);
  border-bottom: 1px solid var(--color-hairline);
}
.modal-title { font: var(--text-title-sm); color: var(--color-ink); }
.modal-close {
  display: flex; align-items: center; justify-content: center;
  width: 36px; height: 36px; border: none; border-radius: var(--radius-sm);
  background: transparent; color: var(--color-muted); cursor: pointer;
  transition: all 0.15s ease;
}
.modal-close:hover { background: var(--color-surface-card); color: var(--color-ink); }

.modal-body {
  padding: var(--space-xl);
  display: flex; flex-direction: column; gap: var(--space-lg);
}

/* --- 输入框 — 匹配登录/对话风格 --- */
.field-group { display: flex; flex-direction: column; gap: var(--space-xs); }
.field-label { font: var(--text-caption); font-weight: 500; color: var(--color-muted); padding-left: 2px; }

.input-row {
  display: flex; align-items: center;
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-md);
  padding: 4px 14px; height: 44px;
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
}
.input-row:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(204, 120, 92, 0.12);
}
.input-row:hover:not(:focus-within) { border-color: var(--color-primary); }

.native-input {
  flex: 1; border: none; outline: none; background: transparent;
  font: var(--text-body-md); color: var(--color-ink);
  min-width: 0; padding: 0;
}
.native-input::placeholder { color: var(--color-muted-soft); }
</style>
