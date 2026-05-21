<template>
  <!-- 对话历史页面 -->
  <div class="page-container">
    <!-- 筛选栏 -->
    <el-card shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="8">
          <el-select
            v-model="queryParams.kb_id"
            placeholder="按知识库筛选"
            clearable
            @change="loadList"
            style="width: 100%"
          >
            <el-option
              v-for="kb in kbOptions"
              :key="kb.id"
              :label="kb.kb_name"
              :value="kb.id"
            />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <!-- 历史记录表格 -->
    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="question" label="问题" min-width="250" show-overflow-tooltip />
        <el-table-column prop="answer" label="回答" min-width="250" show-overflow-tooltip />
        <el-table-column prop="kb_name" label="知识库" width="110" />
        <el-table-column label="命中" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.hit_kb ? 'success' : 'warning'" size="small">{{ row.hit_kb ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="反馈" width="70" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.feedback === 'useful'" type="success" size="small">有用</el-tag>
            <el-tag v-else-if="row.feedback === 'useless'" type="danger" size="small">无用</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="response_time_ms" label="耗时" width="70" align="center">
          <template #default="{ row }">{{ row.response_time_ms ? row.response_time_ms + 'ms' : '-' }}</template>
        </el-table-column>
        <el-table-column prop="username" label="提问者" width="90" />
        <el-table-column prop="create_time" label="时间" width="160" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="loadList"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="对话详情" width="650px">
      <div class="detail-content" v-if="currentChat">
        <div class="detail-item">
          <div class="detail-label">提问：</div>
          <div class="detail-value question">{{ currentChat.question }}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">回答：</div>
          <div class="detail-value answer">{{ currentChat.answer }}</div>
        </div>
        <div class="detail-item" v-if="currentChat.source_docs?.length">
          <div class="detail-label">参考来源：</div>
          <div class="detail-value">
            <el-tag
              v-for="(src, i) in currentChat.source_docs"
              :key="i"
              size="small"
              class="source-tag"
            >
              {{ src.file_name }}
            </el-tag>
          </div>
        </div>
        <div class="detail-item">
          <div class="detail-label">知识库：</div>
          <div class="detail-value">{{ currentChat.kb_name }}</div>
        </div>
        <div class="detail-item" v-if="currentChat.response_time_ms">
          <div class="detail-label">响应时间：</div>
          <div class="detail-value">{{ currentChat.response_time_ms }}ms</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">命中知识库：</div>
          <div class="detail-value">
            <el-tag :type="currentChat.hit_kb ? 'success' : 'warning'" size="small">
              {{ currentChat.hit_kb ? '是' : '否（兜底回答）' }}
            </el-tag>
          </div>
        </div>
        <div class="detail-item" v-if="currentChat.retrieved_docs?.length">
          <div class="detail-label">检索结果：</div>
          <div class="detail-value">
            <div v-for="(doc, i) in currentChat.retrieved_docs" :key="i" class="retrieved-row">
              <el-tag size="small" type="info">#{{ i + 1 }} {{ doc.file_name }}</el-tag>
              <span class="similarity-text">相似度 {{ (doc.similarity * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>
        <div class="detail-item" v-if="currentChat.feedback">
          <div class="detail-label">用户反馈：</div>
          <div class="detail-value">
            <el-tag :type="currentChat.feedback === 'useful' ? 'success' : 'danger'" size="small">
              {{ currentChat.feedback === 'useful' ? '有用' : '无用' }}
            </el-tag>
            <span v-if="currentChat.feedback_reason" class="feedback-reason">{{ currentChat.feedback_reason }}</span>
          </div>
        </div>
        <div class="detail-item">
          <div class="detail-label">时间：</div>
          <div class="detail-value">{{ currentChat.create_time }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 对话历史页面
 * 展示用户的历史问答记录，支持按知识库筛选和查看详情
 */
import { ref, reactive, onMounted } from 'vue'
import { getChatHistory } from '../api/chat'
import { getAllKB } from '../api/knowledge'

const loading = ref(false)
const detailVisible = ref(false)
const tableData = ref([])
const total = ref(0)
const kbOptions = ref([])
const currentChat = ref(null)

const queryParams = reactive({ page: 1, page_size: 10, kb_id: null })

async function loadKBOptions() {
  const res = await getAllKB()
  kbOptions.value = res.data
}

async function loadList() {
  loading.value = true
  try {
    const res = await getChatHistory(queryParams)
    tableData.value = res.data.list
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function showDetail(row) {
  currentChat.value = row
  detailVisible.value = true
}

onMounted(() => {
  loadKBOptions()
  loadList()
})
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  display: flex;
  gap: 8px;
}

.detail-label {
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
  min-width: 70px;
}

.detail-value {
  color: #606266;
  line-height: 1.6;
  word-break: break-all;
}

.detail-value.question {
  color: #409eff;
  font-weight: 500;
}

.detail-value.answer {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  white-space: pre-wrap;
}

.source-tag {
  margin-right: 6px;
  margin-bottom: 4px;
}

.retrieved-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.similarity-text {
  font-size: 12px;
  color: #909399;
}

.feedback-reason {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.text-muted {
  color: #c0c4cc;
  font-size: 12px;
}
</style>
