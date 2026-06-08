<template>
  <div class="login-page">
    <nav class="top-nav">
      <div class="nav-brand">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 0L13 7L20 10L13 13L10 20L7 13L0 10L7 7Z" fill="var(--color-ink)"/></svg>
        <span class="brand-text">企业AI知识库</span>
      </div>
    </nav>

    <div class="login-content">
      <div class="login-grid">
        <div class="login-hero" :style="{ animation: 'fade-in-up 0.7s ease both' }">
          <p class="hero-eyebrow">私有化部署</p>
          <h1 class="hero-headline">构建你的<br/>企业知识大脑</h1>
          <p class="hero-desc">基于 RAG 技术的内部知识库 AI 问答平台。制度、工艺、流程、技术文档 — 即问即答，来源可溯。</p>
        </div>

        <div class="login-panel" :style="{ animation: 'fade-in-up 0.7s ease both', animationDelay: '150ms' }">
          <div class="panel-header">
            <h4>登录</h4>
            <p class="panel-sub">访问你的企业知识库</p>
          </div>

          <form class="login-form" @submit.prevent="handleLogin">
            <!-- 用户名 -->
            <div class="field-group" :class="{ errored: errors.username }">
              <div class="input-row">
                <svg class="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="10" cy="7" r="4"/><path d="M3 18c0-3.9 3.1-7 7-7s7 3.1 7 7"/>
                </svg>
                <input
                  v-model="form.username"
                  type="text"
                  placeholder="用户名"
                  class="native-input"
                  @input="errors.username = ''"
                />
              </div>
              <span v-if="errors.username" class="field-error">{{ errors.username }}</span>
            </div>

            <!-- 密码 -->
            <div class="field-group" :class="{ errored: errors.password }">
              <div class="input-row">
                <svg class="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="4" y="8" width="12" height="10" rx="2"/><path d="M7 8V6a3 3 0 116 0v2"/>
                  <circle cx="10" cy="13" r="1.2"/>
                </svg>
                <input
                  v-model="form.password"
                  :type="showPwd ? 'text' : 'password'"
                  placeholder="密码"
                  class="native-input"
                  @input="errors.password = ''"
                  @keydown.enter="handleLogin"
                />
                <button type="button" class="toggle-pwd" @click="showPwd = !showPwd" :title="showPwd ? '隐藏密码' : '显示密码'">
                  <svg v-if="!showPwd" width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M2 9s3-6 7-6 7 6 7 6-3 6-7 6-7-6-7-6z"/><circle cx="9" cy="9" r="2.5"/>
                  </svg>
                  <svg v-else width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M6.5 3.5C7.3 3.2 8.1 3 9 3c4 0 7 6 7 6s-.7 1.4-2 2.8M3.5 5C2 6.4 2 9 2 9s3 6 7 6c1.3 0 2.5-.4 3.5-1M2 2l14 14M9 7a2 2 0 012 2"/>
                  </svg>
                </button>
              </div>
              <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
            </div>

            <button type="submit" class="submit-btn" :disabled="loading">
              <span v-if="loading" class="spinner"></span>
              <span v-else>登 录</span>
            </button>
          </form>

          <div class="panel-footer">
            <span>还没有账号？</span>
            <router-link to="/register">立即注册</router-link>
          </div>

          <p v-if="error" class="error-msg">{{ error }}</p>
        </div>
      </div>
    </div>

    <div class="login-footer-bar"></div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = reactive({ username: '', password: '' })
const errors = reactive({ username: '', password: '' })
const loading = ref(false)
const error = ref('')
const showPwd = ref(false)

function validate() {
  let ok = true
  if (!form.username.trim()) { errors.username = '请输入用户名'; ok = false }
  if (!form.password || form.password.length < 6) { errors.password = '密码至少 6 位'; ok = false }
  return ok
}

async function handleLogin() {
  if (!validate()) return
  loading.value = true; error.value = ''
  try {
    await authStore.login(form.username, form.password)
    router.push(route.query.redirect || '/')
  } catch (err) {
    error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally { loading.value = false }
}
</script>

<style scoped>
.login-page { min-height: 100vh; background: var(--color-canvas); display: flex; flex-direction: column; }

/* --- Top Nav --- */
.top-nav { height: 64px; display: flex; align-items: center; padding: 0 var(--space-xl); background: var(--color-canvas); border-bottom: 1px solid var(--color-hairline); }
.nav-brand { display: flex; align-items: center; gap: var(--space-sm); }
.brand-mark { flex-shrink: 0; }
.brand-text { font: var(--text-title-sm); color: var(--color-ink); }

/* --- Hero Grid --- */
.login-content { flex: 1; display: flex; align-items: center; justify-content: center; padding: clamp(24px, 3vw, 64px); }
.login-grid { display: grid; grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.8fr); gap: clamp(32px, 6vw, 120px); width: min(92vw, 1400px); align-items: center; }

.login-hero { padding-right: var(--space-xxl); }
.hero-eyebrow { font: var(--text-caption-upper); color: var(--color-muted); letter-spacing: var(--tracking-caption-upper); text-transform: uppercase; margin-bottom: var(--space-lg); }
.hero-headline { font: var(--text-display-xl); font-size: var(--fs-hero); letter-spacing: var(--tracking-display-xl); margin-bottom: var(--space-lg); color: var(--color-ink); }
.hero-desc { font: var(--text-body-md); color: var(--color-body); max-width: 440px; }

/* --- Panel --- */
.login-panel { background: var(--color-canvas); border: 1px solid var(--color-hairline); border-radius: var(--radius-lg); padding: clamp(28px, 3vw, 48px); }
.panel-header { margin-bottom: var(--space-xl); }
.panel-header h4 { font: var(--text-title-lg); color: var(--color-ink); margin-bottom: var(--space-xxs); }
.panel-sub { font: var(--text-body-sm); color: var(--color-muted); }

/* --- Form — 自主设计的输入行 --- */
.login-form { display: flex; flex-direction: column; }

.field-group { margin-bottom: var(--space-lg); }
.field-group.errored .input-row { border-color: var(--color-error); }

/* 输入行 — 模仿 ChatView textarea 的卡片式包裹 */
.input-row {
  display: flex; align-items: center; gap: var(--space-sm);
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-md);
  padding: 4px 14px;
  height: 46px;
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
}
.input-row:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(204, 120, 92, 0.12);
}
.input-row:hover:not(:focus-within) { border-color: var(--color-primary); }

/* 图标 */
.input-icon { flex-shrink: 0; color: var(--color-muted); }

/* 原生输入 */
.native-input {
  flex: 1; border: none; outline: none; background: transparent;
  font: var(--text-body-md); color: var(--color-ink);
  min-width: 0; padding: 0;
}
.native-input::placeholder { color: var(--color-muted-soft); }
/* 自动填充覆盖 */
.native-input:-webkit-autofill {
  -webkit-box-shadow: 0 0 0 30px var(--color-canvas) inset !important;
  -webkit-text-fill-color: var(--color-ink) !important;
}

/* 密码切换 */
.toggle-pwd {
  flex-shrink: 0; background: none; border: none; cursor: pointer;
  color: var(--color-muted-soft); padding: 4px; display: flex;
  border-radius: var(--radius-sm); transition: color 0.2s;
}
.toggle-pwd:hover { color: var(--color-muted); }

/* 错误提示 */
.field-error { display: block; font: var(--text-caption); color: var(--color-error); margin-top: var(--space-xxs); padding-left: 2px; }

/* 提交按钮 */
.submit-btn {
  width: 100%; margin-top: var(--space-md); height: 46px;
  font: var(--text-button); font-size: var(--fs-button);
  letter-spacing: 0.15em; background: var(--color-primary);
  color: var(--color-on-primary); border: none;
  border-radius: var(--radius-md); cursor: pointer;
  transition: background 0.2s ease;
  display: flex; align-items: center; justify-content: center;
}
.submit-btn:hover:not(:disabled) { background: var(--color-primary-active); }
.submit-btn:disabled { background: var(--color-primary-disabled); color: var(--color-muted); cursor: not-allowed; }

/* Loading spinner */
.spinner { width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.panel-footer { text-align: center; margin-top: var(--space-lg); font: var(--text-body-sm); color: var(--color-muted); }
.panel-footer a { color: var(--color-primary); }
.panel-footer a:hover { color: var(--color-primary-active); }

.error-msg { text-align: center; color: var(--color-error); font: var(--text-body-sm); margin-top: var(--space-md); }

.login-footer-bar { height: 4px; background: var(--color-primary); }

/* --- Responsive --- */
@media (max-width: 768px) {
  .login-grid { grid-template-columns: 1fr; gap: var(--space-xl); }
  .login-hero { text-align: center; padding-right: 0; }
  .hero-headline { font-size: clamp(28px, 8vw, 48px); }
  .hero-desc { margin: 0 auto; }
  .login-panel { max-width: 420px; margin: 0 auto; }
}
@media (min-width: 1600px) {
  .login-grid { width: min(85vw, 1600px); }
}
</style>
