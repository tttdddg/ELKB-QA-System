/**
 * 问答对话API
 */
import request from './index'

/** 发送问题（RAG问答） */
export function askQuestion(data) {
  return request.post('/chat/ask', data, {
    timeout: 3600000
  })
}

/** 获取对话历史列表 */
export function getChatHistory(params) {
  return request.get('/chat/history', { params })
}

/** 获取指定会话的对话记录 */
export function getSessionChats(sessionId) {
  return request.get(`/chat/session/${sessionId}`)
}

/** 提交回答反馈 */
export function submitFeedback(chatId, data) {
  return request.post(`/chat/feedback/${chatId}`, data)
}

/** 重新向量化文档 */
export function reprocessDocument(docId) {
  return request.post(`/document/${docId}/reprocess`)
}
