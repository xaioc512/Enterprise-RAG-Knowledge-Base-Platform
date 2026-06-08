<template>
  <div class="admin-shell">
    <aside class="admin-sidebar">
      <div class="sb-brand"><svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 0L12 7L18 9L12 11L9 18L6 11L0 9L6 7Z" fill="var(--color-primary)"/></svg><span class="sb-name">知识库管理</span></div>
      <nav class="sb-nav">
        <router-link to="/admin/documents" class="sb-link">文档管理</router-link>
        <router-link to="/admin/categories" class="sb-link active">分类管理</router-link>
        <router-link to="/admin/users" class="sb-link">用户管理</router-link>
      </nav>
      <router-link to="/" class="sb-back">← 返回问答</router-link>
    </aside>

    <main class="admin-main">
      <div class="page-head">
        <h1 class="page-title">知识分类</h1>
        <button class="btn-primary" @click="showCreate = true">新建分类</button>
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

    <el-dialog v-model="showCreate" title="新建分类" width="400px">
      <el-form>
        <el-form-item><el-input v-model="newName" placeholder="分类名称" /></el-form-item>
        <el-form-item><el-input v-model="newDesc" type="textarea" placeholder="描述（可选）" /></el-form-item>
        <button class="btn-primary full" @click="handleCreate">创建</button>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'; import { ElMessage } from 'element-plus'; import api from '../api'
const categories = ref([]); const showCreate = ref(false); const newName = ref(''); const newDesc = ref('')
onMounted(async () => { try { categories.value = (await api.get('/categories/')).data } catch {} })
async function handleCreate() { if (!newName.value.trim()) return; try { await api.post('/categories/', null, { params: { name: newName.value, description: newDesc.value } }); ElMessage.success('创建成功'); showCreate.value = false; newName.value = ''; newDesc.value = ''; categories.value = (await api.get('/categories/')).data } catch (err) { ElMessage.error(err.response?.data?.detail || '创建失败') } }
async function handleDelete(id) { try { await api.delete(`/categories/${id}`); ElMessage.success('已删除'); categories.value = (await api.get('/categories/')).data } catch { ElMessage.error('删除失败') } }
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
</style>
