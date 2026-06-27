<template>
  <div class="admin-shell">
    <aside class="admin-sidebar">
      <div class="sb-brand">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 0L12 7L18 9L12 11L9 18L6 11L0 9L6 7Z" fill="var(--color-primary)"/></svg>
        <span class="sb-name">知识库管理</span>
      </div>
      <nav class="sb-nav">
        <router-link to="/admin/documents" class="sb-link active">文档管理</router-link>
        <router-link v-if="authStore.isAdmin" to="/admin/categories" class="sb-link">分类管理</router-link>
        <router-link v-if="authStore.isAdmin" to="/admin/departments" class="sb-link">部门管理</router-link>
        <router-link v-if="authStore.isAdmin" to="/admin/users" class="sb-link">用户管理</router-link>
      </nav>
      <router-link to="/" class="sb-back">← 返回问答</router-link>
    </aside>

    <main class="admin-main">
      <div class="page-head">
        <h1 class="page-title">文档管理</h1>
        <button v-if="authStore.isAdmin" class="btn-primary" @click="showUpload = true">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 2v10M4 6l4-4 4 4M2 12v1.5h12V12"/></svg>
          上传文档
        </button>
      </div>

      <!-- 权限提示 -->
      <div v-if="!authStore.isAdmin" class="notice-bar">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="8" cy="8" r="7"/><path d="M8 4v4M8 12h0"/></svg>
        您只能查看本部门和公开文档，如需上传或删除文档请联系管理员
      </div>

      <!-- 分类筛选 -->
      <div class="filter-bar">
        <button :class="['tab-btn', { active: filterCategory === null }]" @click="filterCategory = null; fetchDocuments()">全部</button>
        <button v-for="cat in categories" :key="cat.id" :class="['tab-btn', { active: filterCategory === cat.id }]" @click="filterCategory = cat.id; fetchDocuments()">{{ cat.name }}</button>
      </div>

      <!-- 文档卡片网格 -->
      <div class="doc-grid" v-loading="loading">
        <div v-for="doc in documents" :key="doc.id" class="doc-card" :style="{ animation: 'fade-in-up 0.4s ease both' }">
          <div class="doc-top">
            <span class="type-badge">{{ doc.file_type.toUpperCase() }}</span>
            <span :class="['vis-badge', doc.visibility]">{{ visLabel(doc.visibility) }}</span>
          </div>
          <h4 class="doc-name" @click="previewDocument(doc)">{{ doc.title }}</h4>
          <div class="doc-meta">
            <span class="meta-tag" v-if="doc.category_id">{{ getCategoryName(doc.category_id) }}</span>
            <span class="meta-tag dept" v-if="doc.department_id">{{ getDeptName(doc.department_id) }}</span>
            <span class="meta-info">{{ doc.chunk_count }} 分块</span>
            <span :class="['status-dot', doc.status]"></span>
          </div>
          <p class="doc-summary" v-if="doc.summary">{{ doc.summary }}</p>
          <div class="doc-keywords" v-if="doc.keywords?.length">
            <span class="kw-tag" v-for="(kw, i) in doc.keywords.slice(0,5)" :key="i">{{ kw }}</span>
          </div>
          <div class="doc-actions">
            <button class="action-link" @click="previewDocument(doc)">预览</button>
            <template v-if="authStore.isAdmin">
              <template v-if="deletingId === doc.id">
                <ConfirmPop title="确定删除此文档？" @confirm="deleteDocument(doc.id); deletingId = null" @cancel="deletingId = null" />
              </template>
              <button v-else class="action-link danger" @click="deletingId = doc.id">删除</button>
            </template>
          </div>
        </div>
        <div v-if="!documents.length && !loading" class="empty-hint">暂无文档</div>
      </div>

      <div class="pagination-wrap" v-if="total > pageSize">
        <div class="pager-row">
          <!-- 上一页 -->
          <button
            class="pager-btn arrow"
            :disabled="currentPage <= 1"
            @click="goToPage(currentPage - 1)"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M10 3L5 8l5 5"/>
            </svg>
          </button>

          <!-- 页码 -->
          <template v-for="p in visiblePages">
            <span v-if="p === '...'" :key="'dots-'+p" class="pager-ellipsis">…</span>
            <button
              v-else
              :key="p"
              class="pager-btn num"
              :class="{ active: p === currentPage }"
              @click="goToPage(p)"
            >{{ p }}</button>
          </template>

          <!-- 下一页 -->
          <button
            class="pager-btn arrow"
            :disabled="currentPage >= totalPages"
            @click="goToPage(currentPage + 1)"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M6 3l5 5-5 5"/>
            </svg>
          </button>

          <!-- 跳转输入 -->
          <span class="jumper-label">跳至</span>
          <div class="jumper-input-wrap">
            <input
              v-model="jumpPage"
              type="text"
              inputmode="numeric"
              class="jumper-input"
              placeholder="页"
              @keydown.enter="handleJump"
              @focus="jumpPage = ''"
              @blur="jumpPage = ''"
            />
          </div>
          <span class="total-hint">/ {{ totalPages }} 页</span>
        </div>
      </div>
    </main>

    <!-- 上传 — 自定义居中模态框 + 背景虚化 -->
    <Teleport to="body">
      <transition name="preview-fade">
        <div v-if="showUpload" class="preview-overlay" @click.self="closeUpload" @keydown.esc="closeUpload">
          <div class="preview-panel upload-panel">
            <!-- 顶部栏 -->
            <div class="preview-topbar">
              <div class="preview-meta">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M8 2v10M4 6l4-4 4 4M2 12v1.5h12V12"/>
                </svg>
                <span class="preview-title">上传文档</span>
              </div>
              <button class="preview-close" @click="closeUpload">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M5 5l10 10M15 5l-10 10"/>
                </svg>
              </button>
            </div>

            <!-- 表单区 -->
            <div class="upload-body">
              <!-- 文件拖拽区 -->
              <div
                class="drop-zone"
                :class="{ dragover: isDragover, hasfile: uploadFile }"
                @dragover.prevent="isDragover = true"
                @dragleave.prevent="isDragover = false"
                @drop.prevent="onDrop"
                @click="triggerFileInput"
              >
                <input
                  ref="fileInputRef"
                  type="file"
                  accept=".pdf,.docx,.md,.txt"
                  class="file-hidden-input"
                  @change="onFileInputChange"
                />
                <template v-if="!uploadFile">
                  <svg width="32" height="32" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" class="drop-icon">
                    <path d="M16 6v14M10 12l6-6 6 6M6 22v3h20v-3"/>
                  </svg>
                  <p class="drop-text">拖拽文件到此处，或点击选择</p>
                  <p class="drop-hint">支持 PDF / Word / Markdown / TXT，最大 50MB</p>
                </template>
                <template v-else>
                  <svg width="28" height="28" viewBox="0 0 28 28" fill="none" stroke="currentColor" stroke-width="1.5" class="drop-icon done">
                    <path d="M4 4h12l4 4v16a1 1 0 01-1 1H4a1 1 0 01-1-1V5a1 1 0 011-1z"/>
                    <path d="M16 4v4h4"/>
                    <path d="M9 16l3 3 5-6"/>
                  </svg>
                  <p class="drop-text done">{{ uploadFile.name }}</p>
                  <p class="drop-hint">{{ formatFileSize(uploadFile.size) }} · 点击更换文件</p>
                </template>
              </div>

              <!-- 分类选择 -->
              <div class="upload-field">
                <label class="field-label">知识分类</label>
                <div class="chip-select">
                  <button
                    v-for="cat in categories"
                    :key="cat.id"
                    :class="['chip-opt', { active: uploadCategory === cat.id }]"
                    @click="uploadCategory = uploadCategory === cat.id ? null : cat.id"
                  >{{ cat.name }}</button>
                </div>
              </div>

              <!-- 可见范围 -->
              <div class="upload-field">
                <label class="field-label">可见范围</label>
                <div class="vis-toggle">
                  <button type="button" :class="['vis-opt', { active: uploadVisibility === 'public' }]" @click="uploadVisibility = 'public'; uploadDeptId = null">
                    <span class="vis-opt-title">公开</span><span class="vis-opt-desc">所有人可见</span>
                  </button>
                  <button type="button" :class="['vis-opt', { active: uploadVisibility === 'department' }]" @click="uploadVisibility = 'department'">
                    <span class="vis-opt-title">部门</span><span class="vis-opt-desc">仅指定部门</span>
                  </button>
                  <button type="button" :class="['vis-opt', { active: uploadVisibility === 'restricted' }]" @click="uploadVisibility = 'restricted'">
                    <span class="vis-opt-title">受限</span><span class="vis-opt-desc">指定多部门</span>
                  </button>
                </div>
              </div>

              <!-- 所属部门 -->
              <div class="upload-field" v-if="uploadVisibility !== 'public'">
                <label class="field-label">{{ uploadVisibility === 'restricted' ? '共享部门' : '所属部门' }}</label>
                <div class="chip-select" v-if="uploadVisibility === 'department'">
                  <button
                    v-for="d in departments"
                    :key="d.id"
                    :class="['chip-opt', { active: uploadDeptId === d.id }]"
                    @click="uploadDeptId = uploadDeptId === d.id ? null : d.id"
                  >{{ d.name }}</button>
                </div>
                <div class="chip-select" v-else>
                  <button
                    v-for="d in departments"
                    :key="d.id"
                    :class="['chip-opt', { active: uploadSharedDeptIds.includes(d.id) }]"
                    @click="toggleSharedDept(d.id)"
                  >{{ d.name }}</button>
                </div>
              </div>

              <!-- 提交 -->
              <button class="btn-primary full upload-submit" :disabled="uploading || !uploadFile" @click="handleUpload">
                <span v-if="uploading" class="spinner-sm"></span>
                <span v-else>确认上传</span>
              </button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>

    <!-- 预览 — 自定义居中模态框 + 背景虚化 -->
    <Teleport to="body">
      <transition name="preview-fade">
        <div v-if="showPreview" class="preview-overlay" @click.self="closePreview" @keydown.esc="closePreview">
          <div class="preview-panel">
            <!-- 顶部栏 -->
            <div class="preview-topbar">
              <div class="preview-meta">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M3 2h6l4 4v8a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1z"/>
                  <path d="M9 2v4h4"/>
                </svg>
                <span class="preview-title">{{ previewTitle }}</span>
                <span class="preview-type-badge">{{ previewFileType }}</span>
              </div>
              <button class="preview-close" @click="closePreview">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M5 5l10 10M15 5l-10 10"/>
                </svg>
              </button>
            </div>

            <!-- 内容区 -->
            <div class="preview-content" v-loading="previewLoading">
              <pre v-if="previewText">{{ previewText }}</pre>
              <div v-else-if="previewLoading" class="preview-loading-hint">加载文档中…</div>
            </div>

            <!-- 底部信息 -->
            <div class="preview-bottombar" v-if="previewText">
              <span>{{ previewCharCount }} 字符</span>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import ConfirmPop from '../components/ConfirmPop.vue'

const authStore = useAuthStore()

const documents = ref([]); const categories = ref([]); const departments = ref([])
const loading = ref(false); const showUpload = ref(false); const showPreview = ref(false)
const deletingId = ref(null)
const uploading = ref(false)
const uploadCategory = ref(null)
const uploadVisibility = ref('public')
const uploadDeptId = ref(null)
const uploadSharedDeptIds = ref([])
const uploadFile = ref(null)
const isDragover = ref(false)
const fileInputRef = ref(null)
const previewTitle = ref(''); const previewText = ref(''); const previewFileType = ref(''); const previewCharCount = ref(0); const previewLoading = ref(false)
const filterCategory = ref(null); const currentPage = ref(1); const pageSize = 12; const total = ref(0); const jumpPage = ref('')

// --- 分页器计算属性 ---
const totalPages = computed(() => Math.ceil(total.value / pageSize) || 1)

const visiblePages = computed(() => {
  const curr = currentPage.value
  const last = totalPages.value
  if (last <= 7) return Array.from({ length: last }, (_, i) => i + 1)

  const pages = []
  pages.push(1)
  if (curr > 3) pages.push('...')

  const start = Math.max(2, curr - 1)
  const end = Math.min(last - 1, curr + 1)
  for (let i = start; i <= end; i++) pages.push(i)

  if (curr < last - 2) pages.push('...')
  pages.push(last)
  return pages
})

function goToPage(p) {
  if (p < 1 || p > totalPages.value) return
  currentPage.value = p
  fetchDocuments()
}

function handleJump() {
  const n = parseInt(jumpPage.value, 10)
  if (isNaN(n) || n < 1 || n > totalPages.value) {
    jumpPage.value = ''
    return
  }
  goToPage(n)
  jumpPage.value = ''
}

onMounted(async () => { await Promise.all([fetchCategories(), fetchDocuments(), fetchDepartments()]) })

async function fetchCategories() { try { categories.value = (await api.get('/categories/')).data } catch {} }
async function fetchDepartments() { try { departments.value = (await api.get('/departments/')).data } catch {} }
async function fetchDocuments() {
  deletingId.value = null
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (filterCategory.value) params.category_id = filterCategory.value
    const res = await api.get('/documents/', { params })
    documents.value = res.data.items; total.value = res.data.total
  } catch { ElMessage.error('获取失败') }
  finally { loading.value = false }
}

function onFileInputChange(e) {
  const f = e.target.files?.[0]
  if (f) uploadFile.value = f
}
function onDrop(e) {
  isDragover.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f) uploadFile.value = f
}
function triggerFileInput() { fileInputRef.value?.click() }
function formatFileSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
function toggleSharedDept(id) {
  const idx = uploadSharedDeptIds.value.indexOf(id)
  if (idx >= 0) uploadSharedDeptIds.value.splice(idx, 1)
  else uploadSharedDeptIds.value.push(id)
}
function closeUpload() {
  showUpload.value = false
  uploadFile.value = null
  uploadCategory.value = null
  uploadVisibility.value = 'public'
  uploadDeptId.value = null
  uploadSharedDeptIds.value = []
}
function onUploadKeydown(e) { if (e.key === 'Escape' && showUpload.value) closeUpload() }
watch(showUpload, (v) => {
  if (v) document.addEventListener('keydown', onUploadKeydown)
  else document.removeEventListener('keydown', onUploadKeydown)
})

async function handleUpload() {
  if (!uploadFile.value) { ElMessage.warning('请选择文件'); return }
  if (uploadVisibility.value !== 'public' && !uploadDeptId.value && uploadSharedDeptIds.value.length === 0) { ElMessage.warning('请选择部门'); return }
  uploading.value = true
  try {
    const form = new FormData()
    form.append('file', uploadFile.value)
    if (uploadCategory.value) form.append('category_id', uploadCategory.value)
    form.append('visibility', uploadVisibility.value)
    if (uploadDeptId.value) form.append('department_id', uploadDeptId.value)
    if (uploadVisibility.value === 'restricted' && uploadSharedDeptIds.value.length) {
      form.append('shared_department_ids', uploadSharedDeptIds.value.join(','))
    }
    await api.post('/documents/upload', form, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 120000 })
    ElMessage.success('上传成功')
    closeUpload()
    fetchDocuments()
  } catch (err) { ElMessage.error(err.response?.data?.detail || '上传失败') }
  finally { uploading.value = false }
}

async function previewDocument(doc) {
  previewTitle.value = doc.title
  previewFileType.value = doc.file_type?.toUpperCase() || ''
  showPreview.value = true
  previewLoading.value = true
  previewText.value = ''
  try {
    const res = await api.get(`/documents/${doc.id}/preview`)
    previewText.value = res.data.content
    previewCharCount.value = res.data.char_count || previewText.value.length
  } catch { ElMessage.error('预览失败') }
  finally { previewLoading.value = false }
}

function closePreview() {
  showPreview.value = false
  previewText.value = ''
  previewCharCount.value = 0
}

function onKeydown(e) { if (e.key === 'Escape' && showPreview.value) closePreview() }
watch(showPreview, (v) => {
  if (v) document.addEventListener('keydown', onKeydown)
  else document.removeEventListener('keydown', onKeydown)
})
onUnmounted(() => document.removeEventListener('keydown', onKeydown))

async function deleteDocument(id) { try { await api.delete(`/documents/${id}`); ElMessage.success('已删除'); fetchDocuments() } catch { ElMessage.error('删除失败') } }

function getCategoryName(id) { return categories.value.find(c => c.id === id)?.name || '' }
function getDeptName(id) { return departments.value.find(d => d.id === id)?.name || '' }
function visLabel(v) { return { public: '公开', department: '部门', restricted: '受限' }[v] || v }
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

.admin-main { flex: 1; display: flex; flex-direction: column; padding: clamp(16px, 2.5vw, 40px); overflow-y: auto; }
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: clamp(16px, 2vw, 32px); }
.page-title { font: var(--text-display-sm); letter-spacing: var(--tracking-display-sm); }

.notice-bar {
  display: flex; align-items: center; gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md); margin-bottom: var(--space-lg);
  background: var(--color-surface-card); color: var(--color-body);
  font: var(--text-body-sm); border-radius: var(--radius-md);
  border: 1px solid var(--color-hairline);
}

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

.doc-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-sm); }
.type-badge { font: var(--text-caption-upper); font-size: 11px; letter-spacing: var(--tracking-caption-upper); color: var(--color-muted); background: var(--color-surface-card); padding: 2px 8px; border-radius: var(--radius-xs); }
.vis-badge { font: var(--text-caption); font-size: 11px; padding: 2px 8px; border-radius: var(--radius-pill); }
.vis-badge.public { background: rgba(63,185,80,0.1); color: var(--color-success); }
.vis-badge.department { background: rgba(204,120,92,0.1); color: var(--color-primary); }
.vis-badge.restricted { background: rgba(210,153,34,0.1); color: var(--color-accent-amber, #d29922); }

.doc-name { font: var(--text-title-sm); color: var(--color-ink); cursor: pointer; margin-bottom: var(--space-sm); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.doc-name:hover { color: var(--color-primary); }
.doc-meta { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-sm); flex-wrap: wrap; }
.meta-tag { font: var(--text-caption); color: var(--color-muted); background: var(--color-surface-card); padding: 2px 8px; border-radius: var(--radius-pill); }
.meta-tag.dept { background: rgba(88,166,255,0.08); color: #58a6ff; }
.meta-info { font: var(--text-caption); color: var(--color-muted-soft); }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--color-muted-soft); }
.status-dot.done { background: var(--color-success); }
.status-dot.processing { background: var(--color-accent-amber, #d29922); }
.status-dot.error { background: var(--color-error); }

.doc-actions { display: flex; gap: var(--space-md); }
.action-link { background: none; border: none; color: var(--color-primary); font: var(--text-caption); cursor: pointer; }
.action-link:hover { color: var(--color-primary-active); }
.action-link.danger { color: var(--color-muted); }
.action-link.danger:hover { color: var(--color-error); }

.empty-hint { grid-column: 1/-1; text-align: center; padding: var(--space-section); color: var(--color-muted); font: var(--text-body-md); }

.pagination-wrap {
  position: sticky;
  bottom: 0;
  margin-top: auto;
  padding: var(--space-md) 0 var(--space-lg);
  background: var(--color-canvas);
  border-top: 1px solid var(--color-hairline);
  display: flex;
  justify-content: center;
  z-index: 10;
}

/* --- 自定义分页器 — 匹配登录/对话输入框风格 --- */
.pager-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 页码按钮 */
.pager-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 34px;
  height: 34px;
  padding: 0 4px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-body);
  font: var(--text-body-sm);
  cursor: pointer;
  transition: all 0.15s ease;
}
.pager-btn:hover:not(:disabled):not(.active) {
  background: var(--color-surface-card);
  color: var(--color-ink);
}
.pager-btn.active {
  background: var(--color-primary);
  color: var(--color-on-primary);
  border-color: var(--color-primary);
}
.pager-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* 箭头按钮 */
.pager-btn.arrow {
  color: var(--color-muted);
}
.pager-btn.arrow:hover:not(:disabled) {
  color: var(--color-ink);
  background: var(--color-surface-card);
}

/* 省略号 */
.pager-ellipsis {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 34px;
  color: var(--color-muted-soft);
  font: var(--text-caption);
  user-select: none;
}

/* --- 跳转输入框 — 模仿登录/对话输入框风格 --- */
.jumper-label {
  margin-left: var(--space-md);
  font: var(--text-caption);
  color: var(--color-muted);
  white-space: nowrap;
}
.jumper-input-wrap {
  display: flex;
  align-items: center;
  margin-left: 6px;
  height: 34px;
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-md);
  padding: 0 8px;
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
}
.jumper-input-wrap:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(204, 120, 92, 0.12);
}
.jumper-input-wrap:hover:not(:focus-within) {
  border-color: var(--color-primary);
}
.jumper-input {
  width: 36px;
  border: none;
  outline: none;
  background: transparent;
  font: var(--text-caption);
  color: var(--color-ink);
  text-align: center;
  padding: 0;
}
.jumper-input::placeholder {
  color: var(--color-muted-soft);
  font-size: 11px;
}
.total-hint {
  margin-left: 8px;
  font: var(--text-caption);
  color: var(--color-muted-soft);
  white-space: nowrap;
}
/* --- 上传模态框 --- */
.upload-panel {
  width: min(92vw, 560px);
}
.upload-body {
  padding: var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  overflow-y: auto;
  max-height: calc(85vh - 60px);
}

/* 文件拖拽区 */
.drop-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-xxl) var(--space-xl);
  border: 2px dashed var(--color-hairline);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  background: var(--color-canvas);
}
.drop-zone:hover,
.drop-zone.dragover {
  border-color: var(--color-primary);
  background: rgba(204, 120, 92, 0.04);
}
.drop-zone.hasfile {
  border-style: solid;
  border-color: var(--color-success);
  background: rgba(93, 184, 114, 0.04);
}
.file-hidden-input {
  display: none;
}
.drop-icon {
  color: var(--color-muted-soft);
  transition: color 0.2s;
}
.drop-zone:hover .drop-icon { color: var(--color-muted); }
.drop-icon.done { color: var(--color-success); }
.drop-text {
  font: var(--text-body-sm);
  color: var(--color-muted);
}
.drop-text.done {
  color: var(--color-ink);
  font-weight: 500;
}
.drop-hint {
  font: var(--text-caption);
  color: var(--color-muted-soft);
}

/* 表单字段 */
.upload-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}
.field-label {
  font: var(--text-caption);
  font-weight: 500;
  color: var(--color-muted);
  padding-left: 2px;
}

/* Chip 选择器 — 替代 el-select */
.chip-select {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.chip-opt {
  padding: 6px 14px;
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-pill);
  background: var(--color-canvas);
  font: var(--text-caption);
  color: var(--color-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}
.chip-opt:hover {
  border-color: var(--color-primary);
  color: var(--color-ink);
}
.chip-opt.active {
  background: var(--color-primary);
  color: var(--color-on-primary);
  border-color: var(--color-primary);
}

/* 可见范围切换 — 保持不变但微调 */
.vis-toggle { display: flex; gap: 8px; }
.vis-opt { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 10px 8px; border: 1px solid var(--color-hairline); border-radius: var(--radius-md); background: var(--color-canvas); cursor: pointer; transition: all 0.15s ease; }
.vis-opt:hover { border-color: var(--color-muted); }
.vis-opt.active { border-color: var(--color-primary); background: rgba(204,120,92,0.04); box-shadow: 0 0 0 1px rgba(204,120,92,0.2); }
.vis-opt-title { font: var(--text-caption); font-weight: 500; color: var(--color-ink); }
.vis-opt-desc { font: var(--text-caption); font-size: 11px; color: var(--color-muted-soft); }

/* 上传提交按钮 */
.upload-submit {
  margin-top: var(--space-sm);
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
}
.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
/* --- 预览模态框 — 背景虚化 + 居中面板 --- */
.preview-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(24px, 4vw, 64px);
  background: rgba(20, 20, 19, 0.45);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

/* 入场/离场动画 */
.preview-fade-enter-active {
  transition: opacity 0.25s ease;
}
.preview-fade-leave-active {
  transition: opacity 0.2s ease;
}
.preview-fade-enter-from,
.preview-fade-leave-to {
  opacity: 0;
}
.preview-fade-enter-active .preview-panel {
  animation: preview-in 0.35s cubic-bezier(0.22, 0.61, 0.36, 1) both;
}
.preview-fade-leave-active .preview-panel {
  animation: preview-out 0.2s ease both;
}

@keyframes preview-in {
  from {
    opacity: 0;
    transform: translateY(24px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
@keyframes preview-out {
  to {
    opacity: 0;
    transform: translateY(12px) scale(0.98);
  }
}

/* 内容面板 */
.preview-panel {
  width: min(92vw, 800px);
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-xl);
  box-shadow: 0 24px 80px rgba(20, 20, 19, 0.18);
  overflow: hidden;
}

/* 顶部栏 */
.preview-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-xl);
  border-bottom: 1px solid var(--color-hairline);
  flex-shrink: 0;
}
.preview-meta {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  min-width: 0;
  color: var(--color-muted);
}
.preview-title {
  font: var(--text-title-sm);
  color: var(--color-ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.preview-type-badge {
  flex-shrink: 0;
  font: var(--text-caption);
  font-size: 10px;
  letter-spacing: 0.08em;
  color: var(--color-muted);
  background: var(--color-surface-card);
  padding: 2px 8px;
  border-radius: var(--radius-xs);
}
.preview-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.15s ease;
}
.preview-close:hover {
  background: var(--color-surface-card);
  color: var(--color-ink);
}

/* 内容区 */
.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-xl) clamp(var(--space-lg), 3vw, var(--space-xxl));
}
.preview-content pre {
  white-space: pre-wrap;
  word-break: break-word;
  font: var(--text-body-md);
  line-height: 1.85;
  color: var(--color-body);
}
.preview-loading-hint {
  text-align: center;
  padding: var(--space-section);
  color: var(--color-muted-soft);
  font: var(--text-body-sm);
}

/* 底部信息 */
.preview-bottombar {
  padding: var(--space-sm) var(--space-xl);
  border-top: 1px solid var(--color-hairline);
  font: var(--text-caption);
  color: var(--color-muted-soft);
  flex-shrink: 0;
}

.doc-summary {
  font: var(--text-body-sm); color: var(--color-body);
  margin-bottom: var(--space-sm); line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}
.doc-keywords { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: var(--space-sm); }
.kw-tag {
  font: var(--text-caption); padding: 1px 8px; background: var(--color-surface-card);
  color: var(--color-muted); border-radius: var(--radius-pill); border: 1px solid var(--color-hairline);
}

</style>
