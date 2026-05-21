"""
RAG问答核心服务
基于LangChain构建检索增强生成（RAG）问答链
使用Ollama的qwen3作为大语言模型
"""
import time
from flask import current_app
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from services.vector_service import VectorService


class RAGService:
    """RAG问答服务类"""

    def __init__(self):
        self.llm = ChatOllama(
            model=current_app.config['OLLAMA_LLM_MODEL'],
            base_url=current_app.config['OLLAMA_BASE_URL'],
            temperature=0.3,
            timeout=3600
        )
        self.vector_service = VectorService()

    def _get_config(self):
        """从SystemConfig读取RAG配置，不存在则使用config.py默认值"""
        from models.system_config import SystemConfig
        return {
            'top_k': SystemConfig.get_int('retriever_top_k', current_app.config['RETRIEVER_TOP_K']),
            'threshold': SystemConfig.get_float('similarity_threshold', 0.0),
            'chunk_size': SystemConfig.get_int('chunk_size', current_app.config['CHUNK_SIZE']),
            'chunk_overlap': SystemConfig.get_int('chunk_overlap', current_app.config['CHUNK_OVERLAP']),
        }

    def _format_docs(self, docs):
        """
        将检索到的文档格式化为上下文文本
        """
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('file_name', '未知来源')
            formatted.append(f"[来源{i}: {source}]\n{doc.page_content}")
        return '\n\n'.join(formatted)

    def _build_retrieved_docs(self, docs_with_scores):
        """
        构建检索结果详情列表（含相似度分数），用于日志记录和前端展示
        Chroma返回的score是距离，转换为相似度: 1/(1+distance)
        """
        retrieved = []
        seen = set()
        for doc, distance in docs_with_scores:
            file_name = doc.metadata.get('file_name', '未知')
            chunk_index = doc.metadata.get('chunk_index', -1)
            similarity = round(1.0 / (1.0 + distance), 4)
            chunk_id = f"doc_{doc.metadata.get('doc_id')}_chunk_{chunk_index}"
            retrieved.append({
                'file_name': file_name,
                'chunk_index': chunk_index,
                'chunk_id': chunk_id,
                'similarity': similarity,
                'distance': round(distance, 4),
                'content_preview': doc.page_content[:200]
            })
            seen.add(file_name)
        return retrieved

    def _extract_source_docs(self, docs):
        """
        提取参考文档来源信息（去重），包含相似度
        """
        sources = []
        seen = set()
        for doc, distance in docs:
            file_name = doc.metadata.get('file_name', '未知')
            chunk_index = doc.metadata.get('chunk_index', -1)
            similarity = round(1.0 / (1.0 + distance), 4)
            sources.append({
                'file_name': file_name,
                'chunk_index': chunk_index,
                'similarity': similarity,
                'content_preview': doc.page_content[:200]
            })
        # 按相似度降序排列
        sources.sort(key=lambda x: x['similarity'], reverse=True)
        return sources

    def ask(self, question, kb_id, template_id=None):
        """
        RAG问答主方法
        :param question: 用户问题
        :param kb_id: 知识库ID
        :param template_id: Prompt模板ID（可选，不传则使用默认模板）
        :return: (answer, source_docs, retrieved_docs, prompt_text, hit_kb)
        """
        config = self._get_config()
        start_time = time.time()

        # 带分数的语义检索
        docs_with_scores = self.vector_service.similarity_search_with_score(
            kb_id, question, top_k=config['top_k']
        )

        # 提取检索结果详情
        retrieved_docs = self._build_retrieved_docs(docs_with_scores)

        # 获取最高相似度
        max_similarity = max(
            (1.0 / (1.0 + distance) for _, distance in docs_with_scores),
            default=0.0
        )

        # 兜底：无结果或最高相似度低于阈值
        fallback_answer = '抱歉，当前知识库中没有找到与您问题相关的可靠依据，请尝试换个方式提问或联系管理员补充相关文档。'
        if not docs_with_scores or max_similarity < config['threshold']:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return fallback_answer, [], retrieved_docs, '', elapsed_ms, False

        # 提取纯docs列表(不含分数)用于格式化上下文
        docs = [doc for doc, _ in docs_with_scores]

        # 加载Prompt模板
        system_prompt, user_prompt = self._load_prompt_template(template_id)

        # 渲染模板变量
        context = self._format_docs(docs)
        system_prompt = system_prompt.replace('{context}', context)
        user_prompt = user_prompt.replace('{question}', question)

        prompt = ChatPromptTemplate.from_messages([
            ('system', system_prompt),
            ('human', user_prompt)
        ])

        # 构建RAG链
        rag_chain = prompt | self.llm | StrOutputParser()

        answer = rag_chain.invoke({})

        # 构建实际prompt文本用于日志记录
        prompt_text = f"[SYSTEM]\n{system_prompt}\n\n[USER]\n{user_prompt}"

        # 提取参考来源
        source_docs = self._extract_source_docs(docs_with_scores)

        elapsed_ms = int((time.time() - start_time) * 1000)

        return answer, source_docs, retrieved_docs, prompt_text, elapsed_ms, True

    def _load_prompt_template(self, template_id=None):
        """加载Prompt模板，支持按template_id或kb_id匹配"""
        from models.prompt_template import PromptTemplate

        if template_id:
            tmpl = PromptTemplate.query.get(template_id)
            if tmpl:
                return tmpl.system_prompt, tmpl.user_prompt

        # 使用默认模板
        default = PromptTemplate.query.filter_by(is_default=1).first()
        if default:
            return default.system_prompt, default.user_prompt

        # 硬编码兜底
        return (
            "你是一个企业内部知识库智能问答助手。请根据以下提供的参考资料来回答用户的问题。\n\n要求：\n1. 仅根据参考资料中的内容来回答问题，不要编造信息\n2. 如果参考资料中没有相关信息，请如实告知用户\n3. 回答要准确、简洁、专业\n4. 使用中文回答\n\n参考资料：\n{context}",
            "{question}"
        )
