<template>
  <div class="admin-shell">
    <aside class="admin-sidebar">
      <div class="sb-brand">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 0L12 7L18 9L12 11L9 18L6 11L0 9L6 7Z" fill="var(--color-primary)"/></svg>
        <span class="sb-name">知识库管理</span>
      </div>
      <nav class="sb-nav">
        <router-link to="/admin/documents" class="sb-link">文档管理</router-link>
        <router-link to="/admin/categories" class="sb-link">分类管理</router-link>
        <router-link to="/admin/departments" class="sb-link active">部门管理</router-link>
        <router-link to="/admin/users" class="sb-link">用户管理</router-link>
      </nav>
      <router-link to="/" class="sb-back">← 返回问答</router-link>
    </aside>

    <main class="admin-main">
      <div class="page-head">
        <div>
          <h1 class="page-title">部门管理</h1>
          <p class="page-desc">{{ departments.length }} 个部门 — 管理组织架构与文档访问权限</p>
        </div>
        <button class="btn-primary" @click="openCreate">
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" stroke="currentColor" stroke-width="2"><path d="M7.5 1v13M1 7.5h13"/></svg>
          新建部门
        </button>
      </div>

    <!-- 新建部门 — 自定义居中模态框 -->
    <Teleport to="body">
      <transition name="modal-fade">
        <div v-if="showCreate" class="modal-overlay" @click.self="resetForm">
          <div class="modal-panel">
            <div class="modal-topbar">
              <span class="modal-title">创建新部门</span>
              <button class="modal-close" @click="resetForm">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M5 5l10 10M15 5l-10 10"/>
                </svg>
              </button>
            </div>
            <div class="modal-body">
              <div class="field-group">
                <label class="field-label">部门名称</label>
                <div class="input-row">
                  <input ref="nameInputRef" v-model="formName" type="text" placeholder="输入部门名称" class="native-input" @keydown.enter="handleCreate" />
                </div>
              </div>
              <div class="field-group">
                <label class="field-label">描述（可选）</label>
                <div class="input-row">
                  <input v-model="formDesc" type="text" placeholder="简要描述部门职责" class="native-input" @keydown.enter="handleCreate" />
                </div>
              </div>
              <div class="modal-actions">
                <button class="btn-confirm" @click="handleCreate">确认创建</button>
                <button class="btn-cancel" @click="resetForm">取消</button>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>

      <!-- 部门卡片 -->
      <div class="dept-grid" v-loading="loading">
        <div v-for="(dept, i) in departments" :key="dept.id" class="dept-card" :style="{ animation: 'fade-in-up 0.4s ease both', animationDelay: `${i * 0.06}s` }">
          <div class="dept-index">{{ String(i + 1).padStart(2, '0') }}</div>
          <div class="dept-body">
            <template v-if="editingId === dept.id">
              <div class="dept-edit-fields">
                <input v-model="editName" class="native-input" @keydown.enter="handleUpdate(dept.id)" />
                <input v-model="editDesc" class="native-input" placeholder="描述" @keydown.enter="handleUpdate(dept.id)" />
              </div>
              <div class="dept-edit-actions">
                <button class="action-save" @click="handleUpdate(dept.id)">保存</button>
                <button class="action-cancel" @click="editingId = null">取消</button>
              </div>
            </template>
            <template v-else>
              <div class="dept-top">
                <h4 class="dept-name">{{ dept.name }}</h4>
                <span class="dept-date">{{ fmtDate(dept.created_at) }}</span>
              </div>
              <p class="dept-desc" v-if="dept.description">{{ dept.description }}</p>
              <p class="dept-desc muted" v-else>暂无描述</p>
            </template>
          </div>
          <div class="dept-actions" v-if="editingId !== dept.id">
            <button class="action-link" @click="startEdit(dept)">编辑</button>
            <template v-if="deletingId === dept.id">
              <ConfirmPop title="确定删除此部门？" @confirm="handleDelete(dept.id); deletingId = null" @cancel="deletingId = null" />
            </template>
            <button v-else class="action-link danger" @click="deletingId = dept.id">删除</button>
          </div>
        </div>
        <div v-if="!departments.length && !loading" class="empty-hint">
          <p>暂无部门，点击上方按钮创建</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import ConfirmPop from '../components/ConfirmPop.vue'

const departments = ref([])
const loading = ref(false)
const showCreate = ref(false)
const formName = ref('')
const formDesc = ref('')
const editingId = ref(null)
const editName = ref('')
const editDesc = ref('')
const deletingId = ref(null)
const nameInputRef = ref(null)

onMounted(fetchDepartments)

async function fetchDepartments() {
  deletingId.value = null
  loading.value = true
  try { departments.value = (await api.get('/departments/')).data } catch {} finally { loading.value = false }
}

function openCreate() {
  showCreate.value = true
  formName.value = ''
  formDesc.value = ''
  nextTick(() => nameInputRef.value?.focus())
}
function resetForm() { showCreate.value = false; editingId.value = null; formName.value = ''; formDesc.value = '' }

function onKeydown(e) { if (e.key === 'Escape' && showCreate.value) resetForm() }
watch(showCreate, (v) => {
  if (v) document.addEventListener('keydown', onKeydown)
  else document.removeEventListener('keydown', onKeydown)
})
onUnmounted(() => document.removeEventListener('keydown', onKeydown))

async function handleCreate() {
  if (!formName.value.trim()) { ElMessage.warning('请输入部门名称'); return }
  try {
    await api.post('/departments/', { name: formName.value, description: formDesc.value })
    ElMessage.success('已创建'); resetForm(); fetchDepartments()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '创建失败') }
}

function startEdit(dept) { editingId.value = dept.id; editName.value = dept.name; editDesc.value = dept.description || '' }

async function handleUpdate(id) {
  if (!editName.value.trim()) { ElMessage.warning('部门名称不能为空'); return }
  try {
    await api.put(`/departments/${id}`, { name: editName.value, description: editDesc.value })
    ElMessage.success('已更新'); editingId.value = null; fetchDepartments()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '更新失败') }
}

async function handleDelete(id) {
  try { await api.delete(`/departments/${id}`); ElMessage.success('已删除'); fetchDepartments() } catch (e) { ElMessage.error(e.response?.data?.detail || '删除失败') }
}

function fmtDate(d) { return d ? new Date(d).toLocaleDateString('zh-CN') : '' }
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
.page-head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: clamp(20px, 2vw, 32px); }
.page-title { font: var(--text-display-sm); letter-spacing: var(--tracking-display-sm); color: var(--color-ink); margin-bottom: var(--space-xxs); }
.page-desc { font: var(--text-body-sm); color: var(--color-muted); }

.btn-primary { display: inline-flex; align-items: center; gap: var(--space-xs); padding: var(--btn-padding); height: var(--btn-height); background: var(--color-primary); color: var(--color-on-primary); border: none; border-radius: var(--btn-radius); font: var(--text-button); cursor: pointer; transition: background var(--transition-fast); }
.btn-primary:hover { background: var(--color-primary-active); }

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

/* --- 输入框 --- */
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
  font: var(--text-body-md); color: var(--color-ink); min-width: 0; padding: 0;
}
.native-input::placeholder { color: var(--color-muted-soft); }

.modal-actions { display: flex; gap: var(--space-sm); }
.btn-confirm { flex: 1; height: 40px; font: var(--text-button); font-weight: 500; background: var(--color-primary); color: var(--color-on-primary); border: none; border-radius: var(--radius-md); cursor: pointer; }
.btn-confirm:hover { background: var(--color-primary-active); }
.btn-cancel { flex: 1; height: 40px; font: var(--text-body-sm); background: var(--color-canvas); color: var(--color-muted); border: 1px solid var(--color-hairline); border-radius: var(--radius-md); cursor: pointer; }
.btn-cancel:hover { border-color: var(--color-muted); color: var(--color-ink); }

/* --- 部门卡片 --- */
.dept-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(clamp(340px, 32vw, 480px), 1fr)); gap: var(--space-md); }
.dept-card {
  display: flex; gap: var(--space-md); padding: var(--space-lg);
  background: var(--color-canvas); border: 1px solid var(--color-hairline);
  border-radius: var(--radius-lg); align-items: flex-start;
  transition: box-shadow var(--transition-fast), border-color var(--transition-fast);
}
.dept-card:hover { box-shadow: var(--shadow-hover); border-color: var(--color-primary); }
.dept-index { font: var(--text-display-sm); font-size: 32px; color: var(--color-hairline); flex-shrink: 0; line-height: 1; min-width: 42px; }
.dept-body { flex: 1; min-width: 0; }
.dept-top { display: flex; align-items: baseline; justify-content: space-between; gap: var(--space-sm); margin-bottom: var(--space-xxs); }
.dept-name { font: var(--text-title-sm); color: var(--color-ink); }
.dept-date { font: var(--text-caption); color: var(--color-muted-soft); white-space: nowrap; }
.dept-desc { font: var(--text-body-sm); color: var(--color-body); line-height: 1.5; }
.dept-desc.muted { color: var(--color-muted-soft); font-style: italic; }
.dept-actions { display: flex; flex-direction: column; gap: var(--space-xs); flex-shrink: 0; }
.dept-edit-fields { display: flex; flex-direction: column; gap: var(--space-sm); margin-bottom: var(--space-sm); }
.dept-edit-fields .native-input { border: 1px solid var(--color-primary); border-radius: var(--radius-sm); padding: 6px 10px; font: var(--text-body-md); color: var(--color-ink); background: var(--color-canvas); outline: none; }
.dept-edit-actions { display: flex; gap: var(--space-xs); }
.action-save { height: 28px; padding: 0 14px; background: var(--color-primary); color: var(--color-on-primary); border: none; border-radius: var(--radius-sm); font: var(--text-caption); cursor: pointer; }
.action-save:hover { background: var(--color-primary-active); }
.action-cancel { height: 28px; padding: 0 12px; background: transparent; color: var(--color-muted); border: 1px solid var(--color-hairline); border-radius: var(--radius-sm); font: var(--text-caption); cursor: pointer; }
.action-cancel:hover { border-color: var(--color-muted); color: var(--color-ink); }

.action-link { background: none; border: none; color: var(--color-primary); font: var(--text-caption); cursor: pointer; padding: 2px 0; }
.action-link:hover { color: var(--color-primary-active); }
.action-link.danger { color: var(--color-muted); }
.action-link.danger:hover { color: var(--color-error); }

.empty-hint { grid-column: 1/-1; text-align: center; padding: var(--space-section); color: var(--color-muted); font: var(--text-body-md); }

@media (max-width: 768px) { .panel-body { flex-direction: column; } }
</style>
