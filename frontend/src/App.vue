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

/* --- Pagination 分页 — 强制横向布局 --- */
.el-pagination {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  justify-content: center !important;
  flex-wrap: wrap !important;
  gap: 4px !important;
}
.el-pagination .btn-prev,
.el-pagination .btn-next,
.el-pagination .el-pager {
  display: inline-flex !important;
  flex-shrink: 0 !important;
}
.el-pagination .el-pager {
  flex-direction: row !important;
  gap: 4px !important;
}
.el-pagination .el-pager li {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  float: none !important;
}
.el-pagination button {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

/* --- Pagination 跳转输入框 --- */
.el-pagination__jump {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  margin-left: 12px !important;
  font: var(--text-caption) !important;
  color: var(--color-muted) !important;
}
.el-pagination__jump .el-input {
  width: 56px !important;
}
.el-pagination__jump .el-input__wrapper {
  height: 32px !important;
  padding: 0 6px !important;
  background: var(--color-canvas) !important;
  border: 1px solid var(--color-hairline) !important;
  border-radius: var(--radius-sm) !important;
  box-shadow: none !important;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.el-pagination__jump .el-input__wrapper:hover {
  border-color: var(--color-muted) !important;
}
.el-pagination__jump .el-input__wrapper.is-focus {
  border-color: var(--color-primary) !important;
  box-shadow: 0 0 0 3px rgba(204,120,92,0.12) !important;
}
.el-pagination__jump .el-input__inner {
  text-align: center !important;
  font: var(--text-caption) !important;
  color: var(--color-ink) !important;
  height: 30px !important;
  line-height: 30px !important;
  padding: 0 !important;
}
.el-pagination__jump .el-input__inner::placeholder {
  color: var(--color-muted-soft) !important;
  font-size: 11px !important;
}
/* 隐藏"前往"按钮，用回车替代 */
.el-pagination__jump .el-pagination__goto {
  display: none !important;
}

/* --- Popconfirm 弹窗 — Claude editorial 风格 --- */
/* 修复 popper 容器宽度限制导致文字换行 */
.el-popper.el-popover {
  min-width: max-content !important;
  width: auto !important;
  max-width: none !important;
}
.el-popconfirm {
  background: var(--color-canvas) !important;
  border: 1px solid var(--color-hairline) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: 0 4px 24px rgba(20,20,19,0.10) !important;
  padding: var(--space-lg) var(--space-xl) !important;
  min-width: max-content !important;
  width: auto !important;
}
.el-popconfirm__main {
  display: flex !important;
  align-items: center !important;
  gap: var(--space-sm) !important;
  margin-bottom: var(--space-md) !important;
  white-space: nowrap !important;          /* 强制单行 */
  flex-wrap: nowrap !important;
}
.el-popconfirm__icon {
  flex-shrink: 0 !important;
  color: var(--color-warning) !important;
  font-size: 18px !important;
  margin: 0 !important;
}
/* 标题文字 — Element Plus 渲染为纯文本节点，用 .el-popconfirm__main 统一控制 */
.el-popconfirm__main {
  font: var(--text-body-sm) !important;
  color: var(--color-ink) !important;
}
.el-popconfirm__action {
  display: flex !important;
  justify-content: flex-start !important;  /* 按钮靠左 */
  gap: var(--space-sm) !important;
  margin-top: var(--space-sm) !important;
}
/* 确定按钮 — 珊瑚色，在左边 */
.el-popconfirm__action .el-button--primary {
  order: 0 !important;
  height: 32px !important;
  padding: 0 20px !important;
  font: var(--text-caption) !important;
  font-weight: 500 !important;
  background: var(--color-primary) !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  color: var(--color-on-primary) !important;
}
.el-popconfirm__action .el-button--primary:hover {
  background: var(--color-primary-active) !important;
}
/* 取消按钮 — 右边，hairline 风格 */
.el-popconfirm__action .el-button--small:not(.el-button--primary) {
  height: 32px !important;
  padding: 0 16px !important;
  font: var(--text-caption) !important;
  background: var(--color-canvas) !important;
  border: 1px solid var(--color-hairline) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--color-muted) !important;
  margin-left: 0 !important;
}
.el-popconfirm__action .el-button--small:not(.el-button--primary):hover {
  border-color: var(--color-muted) !important;
  color: var(--color-ink) !important;
}
</style>
