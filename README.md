### 企业内部知识库Agent系统
技术栈：Python Flask+RAG架构+MySQL+SChromaDB向量数据库+Vue 3+Vite+Element Plus+Pinia

完成初步构建，一次性打包上传

进一步新增功能中...


5.21新增：

引用来源展示  已完成 — ChatMessage.vue 展示来源文件名和相似度                            
无答案兜底机制  已完成 — rag_service.py:117 相似度低于阈值时返回兜底回答                     
检索结果可视化  已完成 — 消息气泡中可展开 Top-K 召回详情（文件名、相似度、预览）           
top-k   已完成 — SystemConfig 模型 + SystemConfig.vue 后台页面                        
问答日志记录   已完成 — ChatHistory 扩展了                                                   
用户反馈功能   已完成 — 有用/无用按钮 + 反馈接口 chat.py                
知识库权限隔离  已完成 — KBPermission 模型 + 权限检查 + KBPermission.vue 页面 
文档重新向量化  已完成 — document.py:126 /reprocess 接口，先删旧向量再重建    
文档删除同步删除向量 已完成 — document.py:177 级联删除向量 + 物理文件 + 数据库记录 
Prompt 模板管理 已完成 — PromptTemplate 模型 + 管理页面 + 问答时可选模板 
