<template>
  <div class="register-page">
    <nav class="top-nav">
      <div class="nav-brand">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 0L13 7L20 10L13 13L10 20L7 13L0 10L7 7Z" fill="var(--color-ink)"/></svg>
        <span class="brand-text">企业AI知识库</span>
      </div>
    </nav>

    <div class="register-content">
      <div class="register-panel" :style="{ animation: 'fade-in-up 0.7s ease both' }">
        <div class="panel-header">
          <h4>创建账号</h4>
          <p class="panel-sub">注册后即可使用 AI 知识库问答</p>
        </div>

        <form class="register-form" @submit.prevent="handleRegister">
          <div class="field-group" :class="{ errored: errors.username }">
            <div class="input-row">
              <svg class="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="10" cy="7" r="4"/><path d="M3 18c0-3.9 3.1-7 7-7s7 3.1 7 7"/></svg>
              <input v-model="form.username" type="text" placeholder="用户名" class="native-input" @input="errors.username = ''" />
            </div>
            <span v-if="errors.username" class="field-error">{{ errors.username }}</span>
          </div>

          <div class="field-group" :class="{ errored: errors.email }">
            <div class="input-row">
              <svg class="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="4" width="16" height="12" rx="2"/><path d="M2 4l8 6 8-6"/></svg>
              <input v-model="form.email" type="email" placeholder="邮箱（选填）" class="native-input" @input="errors.email = ''" />
            </div>
            <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
          </div>

          <div class="field-group" :class="{ errored: errors.password }">
            <div class="input-row">
              <svg class="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="8" width="12" height="10" rx="2"/><path d="M7 8V6a3 3 0 116 0v2"/><circle cx="10" cy="13" r="1.2"/></svg>
              <input v-model="form.password" :type="showPwd1 ? 'text' : 'password'" placeholder="密码（至少 6 位）" class="native-input" @input="errors.password = ''" />
              <button type="button" class="toggle-pwd" @click="showPwd1 = !showPwd1">
                <svg v-if="!showPwd1" width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 9s3-6 7-6 7 6 7 6-3 6-7 6-7-6-7-6z"/><circle cx="9" cy="9" r="2.5"/></svg>
                <svg v-else width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6.5 3.5C7.3 3.2 8.1 3 9 3c4 0 7 6 7 6s-.7 1.4-2 2.8M3.5 5C2 6.4 2 9 2 9s3 6 7 6c1.3 0 2.5-.4 3.5-1M2 2l14 14M9 7a2 2 0 012 2"/></svg>
              </button>
            </div>
            <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
          </div>

          <div class="field-group" :class="{ errored: errors.confirm }">
            <div class="input-row">
              <svg class="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="8" width="12" height="10" rx="2"/><path d="M7 8V6a3 3 0 116 0v2"/><path d="M8 13l1.5 1.5L12 12"/></svg>
              <input v-model="form.confirmPassword" :type="showPwd2 ? 'text' : 'password'" placeholder="确认密码" class="native-input" @input="errors.confirm = ''" @keydown.enter="handleRegister" />
              <button type="button" class="toggle-pwd" @click="showPwd2 = !showPwd2">
                <svg v-if="!showPwd2" width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 9s3-6 7-6 7 6 7 6-3 6-7 6-7-6-7-6z"/><circle cx="9" cy="9" r="2.5"/></svg>
                <svg v-else width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6.5 3.5C7.3 3.2 8.1 3 9 3c4 0 7 6 7 6s-.7 1.4-2 2.8M3.5 5C2 6.4 2 9 2 9s3 6 7 6c1.3 0 2.5-.4 3.5-1M2 2l14 14M9 7a2 2 0 012 2"/></svg>
              </button>
            </div>
            <span v-if="errors.confirm" class="field-error">{{ errors.confirm }}</span>
          </div>

          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>注 册</span>
          </button>
        </form>

        <div class="panel-footer">
          <span>已有账号？</span>
          <router-link to="/login">立即登录</router-link>
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({ username: '', email: '', password: '', confirmPassword: '' })
const errors = reactive({ username: '', email: '', password: '', confirm: '' })
const loading = ref(false)
const error = ref('')
const showPwd1 = ref(false)
const showPwd2 = ref(false)

function validate() {
  let ok = true
  if (!form.username.trim()) { errors.username = '请输入用户名'; ok = false }
  else if (form.username.length < 2) { errors.username = '用户名至少 2 个字符'; ok = false }
  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { errors.email = '邮箱格式不正确'; ok = false }
  if (!form.password || form.password.length < 6) { errors.password = '密码至少 6 位'; ok = false }
  if (form.password !== form.confirmPassword) { errors.confirm = '两次密码不一致'; ok = false }
  return ok
}

async function handleRegister() {
  if (!validate()) return
  loading.value = true; error.value = ''
  try {
    await authStore.register(form.username, form.password, form.email || null)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || '注册失败，请稍后重试'
  } finally { loading.value = false }
}
</script>

<style scoped>
.register-page { min-height: 100vh; background: var(--color-canvas); display: flex; flex-direction: column; }
.top-nav { height: 64px; display: flex; align-items: center; padding: 0 var(--space-xl); background: var(--color-canvas); border-bottom: 1px solid var(--color-hairline); }
.nav-brand { display: flex; align-items: center; gap: var(--space-sm); }
.brand-text { font: var(--text-title-sm); color: var(--color-ink); }

.register-content { flex: 1; display: flex; align-items: center; justify-content: center; padding: clamp(24px, 3vw, 64px); }
.register-panel {
  width: 420px; max-width: 90vw; background: var(--color-canvas);
  border: 1px solid var(--color-hairline); border-radius: var(--radius-lg);
  padding: clamp(28px, 3vw, 48px);
}
.panel-header { margin-bottom: var(--space-xl); }
.panel-header h4 { font: var(--text-title-lg); color: var(--color-ink); margin-bottom: var(--space-xxs); }
.panel-sub { font: var(--text-body-sm); color: var(--color-muted); }

/* --- 输入行 — 与 ChatView 一致的卡片式风格 --- */
.register-form { display: flex; flex-direction: column; }
.field-group { margin-bottom: var(--space-lg); }
.field-group.errored .input-row { border-color: var(--color-error); }

.input-row {
  display: flex; align-items: center; gap: var(--space-sm);
  background: var(--color-canvas); border: 1px solid var(--color-hairline);
  border-radius: var(--radius-md); padding: 4px 14px; height: 46px;
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
}
.input-row:focus-within { border-color: var(--color-primary); box-shadow: 0 0 0 3px rgba(204,120,92,0.12); }
.input-row:hover:not(:focus-within) { border-color: var(--color-primary); }

.input-icon { flex-shrink: 0; color: var(--color-muted); }

.native-input {
  flex: 1; border: none; outline: none; background: transparent;
  font: var(--text-body-md); color: var(--color-ink); min-width: 0; padding: 0;
}
.native-input::placeholder { color: var(--color-muted-soft); }
.native-input:-webkit-autofill { -webkit-box-shadow: 0 0 0 30px var(--color-canvas) inset !important; -webkit-text-fill-color: var(--color-ink) !important; }

.toggle-pwd { flex-shrink: 0; background: none; border: none; cursor: pointer; color: var(--color-muted-soft); padding: 4px; display: flex; border-radius: var(--radius-sm); transition: color 0.2s; }
.toggle-pwd:hover { color: var(--color-muted); }

.field-error { display: block; font: var(--text-caption); color: var(--color-error); margin-top: var(--space-xxs); padding-left: 2px; }

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
.spinner { width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.panel-footer { text-align: center; margin-top: var(--space-lg); font: var(--text-body-sm); color: var(--color-muted); }
.panel-footer a { color: var(--color-primary); }
.error-msg { text-align: center; color: var(--color-error); font: var(--text-body-sm); margin-top: var(--space-md); }
</style>
