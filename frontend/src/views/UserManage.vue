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
        <h1 class="page-title">用户管理</h1>
        <button class="btn-primary" @click="showCreate = true">创建用户</button>
      </div>
      <div class="user-table">
        <el-table :data="users" v-loading="loading" empty-text="暂无用户">
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column label="角色" width="100"><template #default="{ row }"><span :class="['role-tag', row.role]">{{ row.role === 'admin' ? '管理员' : '用户' }}</span></template></el-table-column>
          <el-table-column label="状态" width="80"><template #default="{ row }"><span class="status-dot" :class="{ active: row.is_active }"></span></template></el-table-column>
          <el-table-column label="操作" width="100"><template #default="{ row }"><el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)"><template #reference><button class="action-link danger">删除</button></template></el-popconfirm></template></el-table-column>
        </el-table>
      </div>
    </main>
    <el-dialog v-model="showCreate" title="创建用户" width="400px">
      <el-form>
        <el-form-item><el-input v-model="newUsername" placeholder="用户名" /></el-form-item>
        <el-form-item><el-input v-model="newPassword" placeholder="密码" type="password" /></el-form-item>
        <el-form-item><el-select v-model="newRole" placeholder="角色"><el-option label="用户" value="user" /><el-option label="管理员" value="admin" /></el-select></el-form-item>
        <button class="btn-primary full" @click="handleCreate">创建</button>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'; import { ElMessage } from 'element-plus'; import api from '../api'
const users = ref([]); const loading = ref(false); const showCreate = ref(false)
const newUsername = ref(''); const newPassword = ref(''); const newRole = ref('user')
onMounted(fetchUsers)
async function fetchUsers() { loading.value = true; try { users.value = (await api.get('/users/')).data.items } catch {} finally { loading.value = false } }
async function handleCreate() { try { await api.post('/users/', { username: newUsername.value, password: newPassword.value, role: newRole.value }); ElMessage.success('已创建'); showCreate.value = false; fetchUsers() } catch (e) { ElMessage.error(e.response?.data?.detail || '创建失败') } }
async function handleDelete(id) { try { await api.delete(`/users/${id}`); ElMessage.success('已删除'); fetchUsers() } catch { ElMessage.error('删除失败') } }
</script>

<style scoped>
.admin-shell { display: flex; min-height: 100vh; background: var(--color-canvas); }
.admin-sidebar { width: clamp(200px, 16vw, 280px); background: var(--color-surface-dark); display: flex; flex-direction: column; padding: clamp(12px, 1.5vw, 24px); flex-shrink: 0; }
.sb-brand { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-xl); }
.sb-name { color: var(--color-on-dark); font: var(--text-title-sm); }
.sb-nav { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.sb-link { padding: var(--space-sm) var(--space-md); border-radius: var(--radius-sm); color: var(--color-on-dark-soft); font: var(--text-body-sm); }
.sb-link:hover, .sb-link.active { background: rgba(255,255,255,0.06); color: var(--color-on-dark); }
.sb-back { color: var(--color-on-dark-soft); font: var(--text-caption); margin-top: var(--space-lg); padding-top: var(--space-md); border-top: 1px solid rgba(255,255,255,0.06); }
.admin-main { flex: 1; padding: var(--space-xl); }
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-xl); }
.page-title { font: var(--text-display-sm); color: var(--color-ink); }
.btn-primary { display: inline-flex; align-items: center; gap: var(--space-xs); padding: var(--btn-padding); height: var(--btn-height); background: var(--color-primary); color: var(--color-on-primary); border: none; border-radius: var(--btn-radius); font: var(--text-button); cursor: pointer; }
.btn-primary:hover { background: var(--color-primary-active); }
.btn-primary.full { width: 100%; justify-content: center; }
.user-table { background: var(--color-canvas); border: 1px solid var(--color-hairline); border-radius: var(--card-radius); overflow: hidden; }
.role-tag { font: var(--text-caption); padding: 2px 8px; border-radius: var(--radius-pill); }
.role-tag.admin { background: var(--color-primary); color: var(--color-on-primary); }
.role-tag.user { background: var(--color-surface-card); color: var(--color-muted); }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--color-error); }
.status-dot.active { background: var(--color-success); }
.action-link { background: none; border: none; color: var(--color-primary); font: var(--text-caption); cursor: pointer; }
.action-link.danger { color: var(--color-muted); }
.action-link.danger:hover { color: var(--color-error); }
</style>
