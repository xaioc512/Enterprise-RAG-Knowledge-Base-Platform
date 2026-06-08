<template>
  <div class="admin-shell">
    <!-- 侧边栏 (Dark Navy) -->
    <aside class="admin-sidebar">
      <div class="sb-brand">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 0L12 7L18 9L12 11L9 18L6 11L0 9L6 7Z" fill="var(--color-primary)"/></svg>
        <span class="sb-name">知识库管理</span>
      </div>
      <nav class="sb-nav">
        <router-link to="/admin/documents" class="sb-link active">文档管理</router-link>
        <router-link to="/admin/categories" class="sb-link">分类管理</router-link>
        <router-link to="/admin/users" class="sb-link">用户管理</router-link>
      </nav>
      <router-link to="/" class="sb-back">← 返回问答</router-link>
    </aside>

    <main class="admin-main">
      <div class="page-head">
        <h1 class="page-title">文档管理</h1>
        <button class="btn-primary" @click="showUpload = true">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 2v10M4 6l4-4 4 4M2 12v1.5h12V12"/></svg>
          上传文档
        </button>
      </div>

      <!-- 分类筛选 -->
      <div class="filter-bar">
        <button :class="['tab-btn', { active: filterCategory === null }]" @click="filterCategory = null; fetchDocuments()">全部</button>
        <button v-for="cat in categories" :key="cat.id" :class="['tab-btn', { active: filterCategory === cat.id }]" @click="filterCategory = cat.id; fetchDocuments()">{{ cat.name }}</button>
      </div>

      <!-- 文档卡片网格 -->
      <div class="doc-grid" v-loading="loading">
        <div v-for="doc in documents" :key="doc.id" class="doc-card" :style="{ animation: 'fade-in-up 0.4s ease both' }">
          <div class="doc-type-icon">
            <span class="type-badge">{{ doc.file_type.toUpperCase() }}</span>
          </div>
          <h4 class="doc-name" @click="previewDocument(doc)">{{ doc.title }}</h4>
          <div class="doc-meta">
            <span class="meta-tag" v-if="doc.category_id">{{ getCategoryName(doc.category_id) }}</span>
            <span class="meta-info">{{ doc.chunk_count }} 分块</span>
            <span :class="['status-dot', doc.status]"></span>
          </div>
          <div class="doc-actions">
            <button class="action-link" @click="previewDocument(doc)">预览</button>
            <el-popconfirm title="确定删除此文档？" @confirm="deleteDocument(doc.id)">
              <template #reference><button class="action-link danger">删除</button></template>
            </el-popconfirm>
          </div>
        </div>
        <div v-if="!documents.length && !loading" class="empty-hint">暂无文档，请上传</div>
      </div>

      <div class="pagination-wrap" v-if="total > pageSize">
        <el-pagination v-model:current-page="currentPage" :page-size="pageSize" :total="total" layout="prev, pager, next" @current-change="fetchDocuments" />
      </div>
    </main>

    <!-- 上传对话框 -->
    <el-dialog v-model="showUpload" title="上传文档" width="480px">
      <el-form>
        <el-form-item>
          <el-upload ref="uploadRef" :auto-upload="false" :limit="1" :on-change="onFileChange" accept=".pdf,.docx,.md,.txt" drag>
            <div class="upload-hint">拖拽文件或点击上传</div>
            <template #tip><div class="upload-tip">PDF / Word / Markdown / TXT</div></template>
          </el-upload>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="uploadCategory" placeholder="选择分类" clearable>
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <button class="btn-primary full" :disabled="uploading" @click="handleUpload">
          {{ uploading ? '上传处理中...' : '确认上传' }}
        </button>
      </el-form>
    </el-dialog>

    <!-- 预览 -->
    <el-dialog v-model="showPreview" :title="previewTitle" width="700px" top="5vh">
      <div class="preview-box" v-loading="previewLoading">
        <pre v-if="previewText">{{ previewText }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const documents = ref([]); const categories = ref([])
const loading = ref(false); const showUpload = ref(false); const showPreview = ref(false)
const uploading = ref(false); const uploadCategory = ref(null); const uploadFile = ref(null)
const previewTitle = ref(''); const previewText = ref(''); const previewLoading = ref(false)
const filterCategory = ref(null); const currentPage = ref(1); const pageSize = 12; const total = ref(0)

onMounted(async () => { await Promise.all([fetchCategories(), fetchDocuments()]) })

async function fetchCategories() { try { categories.value = (await api.get('/categories/')).data } catch {} }
async function fetchDocuments() {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (filterCategory.value) params.category_id = filterCategory.value
    const res = await api.get('/documents/', { params })
    documents.value = res.data.items; total.value = res.data.total
  } catch { ElMessage.error('获取失败') }
  finally { loading.value = false }
}

function onFileChange(file) { uploadFile.value = file.raw }
async function handleUpload() {
  if (!uploadFile.value) { ElMessage.warning('请选择文件'); return }
  uploading.value = true
  try {
    const form = new FormData(); form.append('file', uploadFile.value)
    if (uploadCategory.value) form.append('category_id', uploadCategory.value)
    await api.post('/documents/upload', form, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 120000 })
    ElMessage.success('上传成功'); showUpload.value = false; uploadFile.value = null; fetchDocuments()
  } catch (err) { ElMessage.error(err.response?.data?.detail || '上传失败') }
  finally { uploading.value = false }
}

async function previewDocument(doc) {
  previewTitle.value = doc.title; showPreview.value = true; previewLoading.value = true
  try { previewText.value = (await api.get(`/documents/${doc.id}/preview`)).data.content } catch { ElMessage.error('预览失败') }
  finally { previewLoading.value = false }
}

async function deleteDocument(id) { try { await api.delete(`/documents/${id}`); ElMessage.success('已删除'); fetchDocuments() } catch { ElMessage.error('删除失败') } }

function getCategoryName(id) { return categories.value.find(c => c.id === id)?.name || '' }
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

.admin-main { flex: 1; padding: clamp(16px, 2.5vw, 40px); overflow-y: auto; }
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: clamp(16px, 2vw, 32px); }
.page-title { font: var(--text-display-sm); letter-spacing: var(--tracking-display-sm); }

.btn-primary {
  display: inline-flex; align-items: center; gap: var(--space-xs);
  padding: var(--btn-padding); height: var(--btn-height);
  background: var(--color-primary); color: var(--color-on-primary);
  border: none; border-radius: var(--btn-radius); font: var(--text-button);
  cursor: pointer; transition: background var(--transition-fast);
}
.btn-primary:hover { background: var(--color-primary-active); }
.btn-primary.full { width: 100%; justify-content: center; }

.filter-bar { display: flex; gap: var(--space-xs); margin-bottom: var(--space-xl); flex-wrap: wrap; }
.tab-btn { padding: 8px 14px; border-radius: var(--radius-md); border: none; background: transparent; color: var(--color-muted); font: var(--text-nav); cursor: pointer; transition: all var(--transition-fast); }
.tab-btn:hover, .tab-btn.active { background: var(--color-surface-card); color: var(--color-ink); }

.doc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(clamp(240px, 22vw, 350px), 1fr)); gap: var(--space-md); }
.doc-card {
  padding: var(--space-lg); background: var(--color-canvas);
  border: 1px solid var(--color-hairline); border-radius: var(--radius-lg);
  transition: box-shadow var(--transition-fast);
}
.doc-card:hover { box-shadow: var(--shadow-hover); }
.doc-type-icon { margin-bottom: var(--space-sm); }
.type-badge { font: var(--text-caption-upper); font-size: 11px; letter-spacing: var(--tracking-caption-upper); color: var(--color-muted); background: var(--color-surface-card); padding: 2px 8px; border-radius: var(--radius-xs); }
.doc-name { font: var(--text-title-sm); color: var(--color-ink); cursor: pointer; margin-bottom: var(--space-sm); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.doc-name:hover { color: var(--color-primary); }
.doc-meta { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-sm); }
.meta-tag { font: var(--text-caption); color: var(--color-muted); background: var(--color-surface-card); padding: 2px 8px; border-radius: var(--radius-pill); }
.meta-info { font: var(--text-caption); color: var(--color-muted-soft); }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--color-muted-soft); }
.status-dot.done { background: var(--color-success); }
.status-dot.processing { background: var(--color-accent-amber); }
.status-dot.error { background: var(--color-error); }

.doc-actions { display: flex; gap: var(--space-md); }
.action-link { background: none; border: none; color: var(--color-primary); font: var(--text-caption); cursor: pointer; }
.action-link:hover { color: var(--color-primary-active); }
.action-link.danger { color: var(--color-muted); }
.action-link.danger:hover { color: var(--color-error); }

.empty-hint { grid-column: 1/-1; text-align: center; padding: var(--space-section); color: var(--color-muted); font: var(--text-body-md); }

.pagination-wrap { margin-top: var(--space-xl); display: flex; justify-content: center; }
.upload-hint { color: var(--color-muted); font: var(--text-body-md); padding: var(--space-xl); }
.upload-tip { font: var(--text-caption); color: var(--color-muted-soft); margin-top: var(--space-xs); }
.preview-box { max-height: 70vh; overflow: auto; }
.preview-box pre { white-space: pre-wrap; font: var(--text-body-md); line-height: 1.8; }
</style>
