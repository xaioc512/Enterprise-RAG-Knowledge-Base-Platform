<template>
  <div id="app-root">
    <router-view v-slot="{ Component, route }">
      <transition name="page-fade" mode="out-in">
        <component :is="Component" :key="route.path" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  authStore.restoreSession()
})
</script>

<style>
/* --- Page Transition --- */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.page-fade-enter-from { opacity: 0; transform: translateY(8px); }
.page-fade-leave-to   { opacity: 0; transform: translateY(-8px); }

#app-root {
  min-height: 100vh;
  background: var(--color-canvas);
}

/* --- Element Plus Cream Theme Overrides --- */
:root {
  --el-color-primary: var(--color-primary);
  --el-color-primary-light-3: var(--color-primary-active);
  --el-color-primary-light-5: rgba(204,120,92,0.5);
  --el-color-primary-light-7: rgba(204,120,92,0.3);
  --el-color-primary-light-9: rgba(204,120,92,0.1);
  --el-color-success: var(--color-success);
  --el-color-warning: var(--color-warning);
  --el-color-danger: var(--color-error);
  --el-bg-color: var(--color-canvas);
  --el-bg-color-overlay: var(--color-canvas);
  --el-bg-color-page: var(--color-canvas);
  --el-border-color: var(--color-hairline);
  --el-border-color-light: var(--color-hairline-soft);
  --el-border-color-lighter: var(--color-hairline-soft);
  --el-text-color-primary: var(--color-ink);
  --el-text-color-regular: var(--color-body);
  --el-text-color-secondary: var(--color-muted);
  --el-text-color-placeholder: var(--color-muted-soft);
  --el-fill-color-blank: var(--color-canvas);
  --el-fill-color: var(--color-surface-card);
  --el-fill-color-light: var(--color-surface-soft);
  --el-border-radius-base: var(--radius-md);
  --el-border-radius-small: var(--radius-sm);

  /* Dialog */
  --el-dialog-bg-color: var(--color-canvas);
  --el-dialog-border-radius: var(--radius-lg);

  /* Button */
  --el-button-font-weight: 500;
  --el-button-border-color: var(--color-hairline);

  /* Input */
  --el-input-bg-color: var(--color-canvas);
  --el-input-border-color: var(--color-hairline);
  --el-input-hover-border-color: var(--color-primary);
  --el-input-focus-border-color: var(--color-primary);
  --el-input-placeholder-color: var(--color-muted-soft);

  /* Table */
  --el-table-bg-color: var(--color-canvas);
  --el-table-header-bg-color: var(--color-surface-soft);
  --el-table-row-hover-bg-color: var(--color-surface-card);
  --el-table-border-color: var(--color-hairline);
  --el-table-text-color: var(--color-body);

  /* Tag */
  --el-tag-bg-color: var(--color-surface-card);
  --el-tag-border-color: var(--color-hairline);
  --el-tag-text-color: var(--color-body);

  /* Radio */
  --el-radio-bg-color: var(--color-canvas);
  --el-radio-input-border-color: var(--color-hairline);

  /* Menu */
  --el-menu-bg-color: var(--color-canvas);
  --el-menu-text-color: var(--color-body);
  --el-menu-hover-bg-color: var(--color-surface-card);
}

/* Button primary overrides */
.el-button--primary {
  --el-button-bg-color: var(--color-primary);
  --el-button-border-color: var(--color-primary);
  --el-button-hover-bg-color: var(--color-primary-active);
  --el-button-hover-border-color: var(--color-primary-active);
  --el-button-active-bg-color: var(--color-primary-active);
  --el-button-active-border-color: var(--color-primary-active);
}

/* Global: fix oversized Element Plus SVG icons */
.el-icon {
  --el-icon-size: 16px;
  font-size: var(--el-icon-size) !important;
  width: var(--el-icon-size) !important;
  height: var(--el-icon-size) !important;
}
.el-icon svg {
  width: var(--el-icon-size) !important;
  height: var(--el-icon-size) !important;
}

/* Input prefix/suffix icon sizing */
.el-input__prefix-inner > .el-icon,
.el-input__suffix-inner > .el-icon,
.el-input__prefix > .el-icon,
.el-input__suffix > .el-icon {
  --el-icon-size: 16px;
  font-size: 16px !important;
  width: 16px !important;
  height: 16px !important;
}
.el-input__prefix-inner > .el-icon svg,
.el-input__suffix-inner > .el-icon svg,
.el-input__prefix > .el-icon svg,
.el-input__suffix > .el-icon svg {
  width: 16px !important;
  height: 16px !important;
}

/* Large input: slightly bigger icon */
.el-input--large .el-input__prefix-inner > .el-icon,
.el-input--large .el-input__suffix-inner > .el-icon,
.el-input--large .el-input__prefix > .el-icon,
.el-input--large .el-input__suffix > .el-icon {
  font-size: 18px !important;
  width: 18px !important;
  height: 18px !important;
}
.el-input--large .el-input__prefix-inner > .el-icon svg,
.el-input--large .el-input__suffix-inner > .el-icon svg,
.el-input--large .el-input__prefix > .el-icon svg,
.el-input--large .el-input__suffix > .el-icon svg {
  width: 18px !important;
  height: 18px !important;
}

/* General icon color in inputs */
.el-input__prefix,
.el-input__suffix,
.el-input__prefix-inner,
.el-input__suffix-inner {
  color: var(--color-muted);
}
</style>
