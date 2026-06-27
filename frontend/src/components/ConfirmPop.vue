<template>
  <div class="confirm-pop" :style="{ animation: 'fade-in-up 0.2s ease both' }">
    <span class="confirm-text">{{ title }}</span>
    <div class="confirm-actions">
      <button class="btn-confirm" @click="$emit('confirm')">确定</button>
      <button class="btn-cancel" @click="$emit('cancel')">取消</button>
    </div>
  </div>
</template>

<script setup>
defineProps({ title: { type: String, default: '确定删除？' } })
defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.confirm-pop {
  display: inline-flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 20px rgba(20,20,19,0.10);
  white-space: nowrap;
}
.confirm-text {
  font: var(--text-body-sm);
  color: var(--color-ink);
  white-space: nowrap;
}
.confirm-actions {
  display: flex;
  gap: var(--space-xs);
}
.btn-confirm {
  height: 30px;
  padding: 0 14px;
  font: var(--text-caption);
  font-weight: 500;
  background: var(--color-primary);
  color: var(--color-on-primary);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s ease;
}
.btn-confirm:hover { background: var(--color-primary-active); }

.btn-cancel {
  height: 30px;
  padding: 0 12px;
  font: var(--text-caption);
  background: var(--color-canvas);
  color: var(--color-muted);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-sm);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}
.btn-cancel:hover {
  border-color: var(--color-muted);
  color: var(--color-ink);
}
</style>
