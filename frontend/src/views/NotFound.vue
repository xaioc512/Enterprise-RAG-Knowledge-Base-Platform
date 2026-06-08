<template>
  <div class="nf-page">
    <nav class="top-nav"><div class="nav-brand"><svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 0L13 7L20 10L13 13L10 20L7 13L0 10L7 7Z" fill="var(--color-ink)"/></svg><span class="brand-text">企业AI知识库</span></div></nav>
    <div class="nf-content">
      <h1>页面未找到</h1>
      <p>你访问的页面不存在</p>
      <router-link to="/">← 返回首页</router-link>
    </div>
  </div>
</template>
<style scoped>
.nf-page { min-height: 100vh; background: var(--color-canvas); }
.top-nav { height: 64px; display: flex; align-items: center; padding: 0 var(--space-xl); border-bottom: 1px solid var(--color-hairline); }
.nav-brand { display: flex; align-items: center; gap: var(--space-sm); }
.brand-text { font: var(--text-title-sm); color: var(--color-ink); }
.nf-content { text-align: center; padding: var(--space-section) var(--space-xl); }
.nf-content h1 { font: var(--text-display-lg); margin-bottom: var(--space-md); }
.nf-content p { color: var(--color-muted); margin-bottom: var(--space-lg); }
.nf-content a { color: var(--color-primary); font: var(--text-body-md); }
</style>
