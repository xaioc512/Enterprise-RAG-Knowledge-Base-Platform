<template>
  <div class="admin-shell">
    <aside class="admin-sidebar">
      <div class="sb-brand"><svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 0L12 7L18 9L12 11L9 18L6 11L0 9L6 7Z" fill="var(--color-primary)"/></svg><span class="sb-name">知识库管理</span></div>
      <nav class="sb-nav">
        <router-link to="/admin" class="sb-link">概览</router-link>
        <router-link to="/admin/documents" class="sb-link">文档管理</router-link>
        <router-link to="/admin/categories" class="sb-link">分类管理</router-link>
        <router-link to="/admin/users" class="sb-link active">用户管理</router-link>
      </nav>
      <router-link to="/" class="sb-back">← 返回问答</router-link>
    </aside>

    <main class="admin-main">
      <div class="page-head">
        <div>
          <h1 class="page-title">用户管理</h1>
          <p class="page-desc">{{ users.length }} 个用户</p>
        </div>
        <button class="btn-primary" @click="openCreate">
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" stroke="currentColor" stroke-width="2"><path d="M7.5 1v13M1 7.5h13"/></svg>
          创建用户
        </button>
      </div>

      <!-- 创建面板 -->
      <div v-if="showCreate" class="create-card" :style="{ animation: 'fade-in-up 0.35s ease both' }">
        <h3 class="create-title">创建新用户</h3>
        <form class="create-form" @submit.prevent="handleCreate">
          <div class="create-fields">
            <div class="input-row">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="9" cy="6" r="3.5"/><path d="M3 16c0-3.3 2.7-6 6-6s6 2.7 6 6"/></svg>
              <input v-model="newUsername" type="text" placeholder="用户名" class="native-input" />
            </div>
            <div class="input-row">
              <svg class="input-icon" width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="7" width="12" height="10" rx="2"/><path d="M6 7V5a3 3 0 116 0v2"/></svg>
              <input v-model="newPassword" type="password" placeholder="密码" class="native-input" />
            </div>
            <select v-model="newDeptId" class="native-input dept-select" v-if="newRole === 'user'">
              <option :value="null">选择部门（可选）</option>
              <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
            <div class="role-toggle">
              <button type="button" :class="['role-opt', { active: newRole === 'user' }]" @click="newRole = 'user'">普通用户</button>
              <button type="button" :class="['role-opt', { active: newRole === 'admin' }]" @click="newRole = 'admin'">管理员</button>
            </div>
          </div>
          <div class="create-actions">
            <button type="submit" class="btn-confirm">创建</button>
            <button type="button" class="btn-cancel" @click="showCreate = false">取消</button>
          </div>
        </form>
      </div>

      <!-- 用户卡片网格 -->
      <div class="user-grid" v-loading="loading">
        <div v-for="user in users" :key="user.id" class="user-card" :style="{ animation: 'fade-in-up 0.35s ease both' }">
          <div class="user-avatar" :class="user.role">
            <span>{{ user.username[0]?.toUpperCase() }}</span>
          </div>
          <div class="user-info">
            <div class="user-top">
              <h4 class="user-name">{{ user.username }}</h4>
              <span :class="['user-role', user.role]">{{ user.role === 'admin' ? '管理员' : '用户' }}</span>
              <span class="user-dept" v-if="user.department_id">{{ getDeptName(user.department_id) }}</span>
            </div>
            <p class="user-email" v-if="user.email">{{ user.email }}</p>
            <p class="user-email muted" v-else>未设置邮箱</p>
            <div class="user-meta">
              <span class="meta-dot" :class="{ active: user.is_active }"></span>
              <span class="meta-text">{{ user.is_active ? '正常' : '禁用' }}</span>
              <span class="meta-divider">·</span>
              <span class="meta-text">{{ fmtDate(user.created_at) }}</span>
            </div>
          </div>
          <div class="user-action">
            <template v-if="deletingId === user.id">
              <ConfirmPop title="确定删除此用户？" @confirm="handleDelete(user.id); deletingId = null" @cancel="deletingId = null" />
            </template>
            <button v-else class="delete-btn" @click="deletingId = user.id" title="删除用户">
              <svg width="15" height="15" viewBox="0 0 15 15" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 4h11M5 4V3a1 1 0 011-1h3a1 1 0 011 1v1M6 7v4M9 7v4M3 4l1 9h7l1-9"/></svg>
            </button>
          </div>
        </div>
        <div v-if="!users.length && !loading" class="empty-hint">暂无用户，点击上方按钮创建</div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'; import { ElMessage } from 'element-plus'; import api from '../api'
import ConfirmPop from '../components/ConfirmPop.vue'

const users = ref([]); const departments = ref([]); const loading = ref(false); const showCreate = ref(false); const deletingId = ref(null)
const newUsername = ref(''); const newPassword = ref(''); const newRole = ref('user'); const newDeptId = ref(null)

onMounted(async () => { await Promise.all([fetchUsers(), fetchDepartments()]) })

async function fetchUsers() { deletingId.value = null; loading.value = true; try { users.value = (await api.get('/users/')).data.items } catch {} finally { loading.value = false } }
async function fetchDepartments() { try { departments.value = (await api.get('/departments/')).data } catch {} }

function openCreate() { showCreate.value = true; newUsername.value = ''; newPassword.value = ''; newRole.value = 'user'; newDeptId.value = null }

async function handleCreate() {
  if (!newUsername.value.trim() || !newPassword.value) { ElMessage.warning('用户名和密码不能为空'); return }
  const payload = { username: newUsername.value, password: newPassword.value, role: newRole.value }
  if (newRole.value === 'user' && newDeptId.value) payload.department_id = newDeptId.value
  try { await api.post('/users/', payload); ElMessage.success('已创建'); showCreate.value = false; fetchUsers() } catch (e) { ElMessage.error(e.response?.data?.detail || '创建失败') }
}

function getDeptName(id) { return departments.value.find(d => d.id === id)?.name || '' }

async function handleDelete(id) { try { await api.delete(`/users/${id}`); ElMessage.success('已删除'); fetchUsers() } catch { ElMessage.error('删除失败') } }

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

/* --- 创建面板 --- */
.create-card { background: var(--color-canvas); border: 1px solid var(--color-hairline); border-radius: var(--radius-lg); padding: var(--space-xl); margin-bottom: var(--space-xl); }
.create-title { font: var(--text-title-sm); color: var(--color-ink); margin-bottom: var(--space-lg); }
.create-fields { display: flex; flex-wrap: wrap; gap: var(--space-md); align-items: center; margin-bottom: var(--space-lg); }
.create-fields .input-row { flex: 1; min-width: 200px; display: flex; align-items: center; gap: var(--space-sm); border: 1px solid var(--color-hairline); border-radius: var(--radius-md); padding: 6px 12px; height: 42px; transition: border-color 0.2s, box-shadow 0.2s; }
.create-fields .input-row:focus-within { border-color: var(--color-primary); box-shadow: 0 0 0 3px rgba(204,120,92,0.12); }
.input-icon { flex-shrink: 0; color: var(--color-muted); }
.native-input { flex: 1; border: none; outline: none; background: transparent; font: var(--text-body-md); color: var(--color-ink); min-width: 0; }
.native-input::placeholder { color: var(--color-muted-soft); }

.dept-select { min-width: 160px; border: 1px solid var(--color-hairline); border-radius: var(--radius-md); padding: 6px 12px; height: 42px; background: var(--color-canvas); font: var(--text-body-md); color: var(--color-ink); outline: none; cursor: pointer; }
.dept-select:focus { border-color: var(--color-primary); }

.role-toggle { display: flex; gap: 2px; background: var(--color-surface-card); border-radius: var(--radius-md); padding: 3px; }
.role-opt { padding: 8px 16px; border: none; background: transparent; font: var(--text-caption); color: var(--color-muted); border-radius: var(--radius-sm); cursor: pointer; transition: all 0.15s ease; }
.role-opt.active { background: var(--color-canvas); color: var(--color-ink); box-shadow: 0 1px 2px rgba(20,20,19,0.06); }

.create-actions { display: flex; gap: var(--space-sm); }
.btn-confirm { height: 36px; padding: 0 24px; font: var(--text-caption); font-weight: 500; background: var(--color-primary); color: var(--color-on-primary); border: none; border-radius: var(--radius-sm); cursor: pointer; }
.btn-confirm:hover { background: var(--color-primary-active); }
.btn-cancel { height: 36px; padding: 0 16px; font: var(--text-caption); background: var(--color-canvas); color: var(--color-muted); border: 1px solid var(--color-hairline); border-radius: var(--radius-sm); cursor: pointer; }
.btn-cancel:hover { border-color: var(--color-muted); color: var(--color-ink); }

/* --- 用户卡片网格 --- */
.user-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(clamp(320px, 30vw, 420px), 1fr)); gap: var(--space-md); }
.user-card { display: flex; gap: var(--space-md); padding: var(--space-lg); background: var(--color-canvas); border: 1px solid var(--color-hairline); border-radius: var(--radius-lg); align-items: flex-start; transition: box-shadow var(--transition-fast); }
.user-card:hover { box-shadow: var(--shadow-hover); }

.user-avatar { width: 40px; height: 40px; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; flex-shrink: 0; font: var(--text-title-sm); font-weight: 600; color: var(--color-muted); background: var(--color-surface-card); }
.user-avatar.admin { background: var(--color-primary); color: var(--color-on-primary); }

.user-info { flex: 1; min-width: 0; }
.user-top { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: 2px; }
.user-name { font: var(--text-title-sm); color: var(--color-ink); }
.user-role { font: var(--text-caption); padding: 1px 8px; border-radius: var(--radius-pill); }
.user-role.admin { background: var(--color-primary); color: var(--color-on-primary); }
.user-role.user { background: var(--color-surface-card); color: var(--color-muted); }
.user-dept { font: var(--text-caption); padding: 1px 8px; border-radius: var(--radius-pill); background: var(--color-accent-blue-subtle, rgba(88,166,255,0.1)); color: var(--color-accent-blue, #58a6ff); }

.user-email { font: var(--text-body-sm); color: var(--color-body); margin-bottom: var(--space-xs); }
.user-email.muted { color: var(--color-muted-soft); }

.user-meta { display: flex; align-items: center; gap: var(--space-xxs); }
.meta-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--color-error); flex-shrink: 0; }
.meta-dot.active { background: var(--color-success); }
.meta-text { font: var(--text-caption); color: var(--color-muted-soft); }
.meta-divider { color: var(--color-hairline); }

.user-action { flex-shrink: 0; display: flex; align-items: center; min-height: 40px; }
.delete-btn { background: none; border: none; color: var(--color-muted-soft); padding: 6px; cursor: pointer; border-radius: var(--radius-sm); transition: all var(--transition-fast); }
.delete-btn:hover { color: var(--color-error); background: rgba(198,69,69,0.06); }

.empty-hint { grid-column: 1/-1; text-align: center; padding: var(--space-section); color: var(--color-muted); font: var(--text-body-md); }

@media (max-width: 768px) { .create-fields { flex-direction: column; } .create-fields .input-row { min-width: 0; } }
</style>
