<template>
  <!-- 对话消息气泡组件 -->
  <div class="message-wrapper" :class="{ 'is-user': isUser }">
    <div class="avatar">
      <el-avatar :size="36" :icon="isUser ? UserFilled : Monitor" :style="avatarStyle" />
    </div>
    <div class="bubble" :class="{ 'user-bubble': isUser, 'ai-bubble': !isUser }">
      <div class="message-text">{{ message.content }}</div>

      <!-- AI回答：响应信息 -->
      <div v-if="!isUser && message.responseTime" class="meta-info">
        <span>响应时间: {{ message.responseTime }}ms</span>
        <span v-if="!message.hitKb" class="no-hit">未命中知识库</span>
      </div>

      <!-- AI回答：检索结果 -->
      <div v-if="!isUser && message.retrieved?.length" class="retrieved-section">
        <div class="section-toggle" @click="showRetrieved = !showRetrieved">
          <el-icon><component :is="showRetrieved ? ArrowDown : ArrowRight" /></el-icon>
          <span>检索详情 (Top-{{ message.retrieved.length }}，最高相似度 {{ topSimilarity }})</span>
        </div>
        <div v-show="showRetrieved" class="retrieved-list">
          <div v-for="(doc, i) in message.retrieved" :key="i" class="retrieved-item">
            <div class="retrieved-header">
              <el-tag size="small" :type="doc.similarity >= 0.7 ? 'success' : doc.similarity >= 0.5 ? 'warning' : 'info'">
                相似度 {{ (doc.similarity * 100).toFixed(1) }}%
              </el-tag>
              <span class="retrieved-source">{{ doc.file_name }} #{{ doc.chunk_index }}</span>
            </div>
            <div class="retrieved-preview">{{ doc.content_preview }}</div>
          </div>
        </div>
      </div>

      <!-- AI回答：参考来源 -->
      <div v-if="!isUser && message.sources?.length" class="sources">
        <div class="sources-title">参考来源：</div>
        <el-tag
          v-for="(src, i) in message.sources"
          :key="i"
          size="small"
          type="info"
          class="source-tag"
        >
          {{ src.file_name }}
          <span v-if="src.similarity !== undefined"> ({{ (src.similarity * 100).toFixed(0) }}%)</span>
        </el-tag>
      </div>

      <!-- AI回答：反馈按钮 -->
      <div v-if="!isUser && message.chatId" class="feedback">
        <span class="feedback-label">这条回答对您有帮助吗？</span>
        <el-button
          :type="message.feedback === 'useful' ? 'success' : 'default'"
          size="small"
          plain
          @click="$emit('feedback', message.chatId, 'useful')"
        >
          <el-icon><Select /></el-icon> 有用
        </el-button>
        <el-button
          :type="message.feedback === 'useless' ? 'danger' : 'default'"
          size="small"
          plain
          @click="$emit('feedback', message.chatId, 'useless')"
        >
          <el-icon><CloseBold /></el-icon> 无用
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { UserFilled, Monitor, ArrowDown, ArrowRight, Select, CloseBold } from '@element-plus/icons-vue'

const props = defineProps({
  message: { type: Object, required: true }
})

defineEmits(['feedback'])

const isUser = computed(() => props.message.role === 'user')
const avatarStyle = computed(() => ({
  backgroundColor: isUser.value ? '#409eff' : '#67c23a'
}))

const showRetrieved = ref(false)
const topSimilarity = computed(() => {
  if (!props.message.retrieved?.length) return '0%'
  const max = Math.max(...props.message.retrieved.map(d => d.similarity || 0))
  return (max * 100).toFixed(1) + '%'
})
</script>

<style scoped>
.message-wrapper {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: flex-start;
}
.message-wrapper.is-user {
  flex-direction: row-reverse;
}
.bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}
.user-bubble {
  background: #409eff;
  color: #fff;
  border-top-right-radius: 4px;
}
.ai-bubble {
  background: #f4f4f5;
  color: #303133;
  border-top-left-radius: 4px;
}
.message-text {
  font-size: 14px;
}
.meta-info {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 12px;
}
.no-hit {
  color: #e6a23c;
}
.retrieved-section {
  margin-top: 8px;
  border-top: 1px solid #e4e7ed;
  padding-top: 6px;
}
.section-toggle {
  font-size: 12px;
  color: #409eff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}
.retrieved-list {
  margin-top: 6px;
}
.retrieved-item {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 8px 10px;
  margin-bottom: 6px;
}
.retrieved-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.retrieved-source {
  font-size: 12px;
  color: #606266;
}
.retrieved-preview {
  font-size: 12px;
  color: #909399;
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
}
.sources {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid #e4e7ed;
}
.sources-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}
.source-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}
.feedback {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 8px;
}
.feedback-label {
  font-size: 12px;
  color: #909399;
}
</style>