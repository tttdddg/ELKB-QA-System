#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chroma向量数据库管理模块
负责向量数据库的初始化、文档向量化、检索等操作
"""

import os
from chromadb import PersistentClient
from chromadb.config import Settings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from config import config

# 获取配置
current_config = config['default']

class ChromaManager:
    """
    Chroma向量数据库管理器
    封装了Chroma的核心操作
    """
    
    def __init__(self):
        """初始化Chroma客户端和Embedding模型"""
        # 确保Chroma数据目录存在
        os.makedirs(current_config.CHROMA_PATH, exist_ok=True)
        
        # 创建Chroma持久化客户端
        self.client = PersistentClient(
            path=current_config.CHROMA_PATH,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 初始化Embedding模型
        self.embedding = HuggingFaceEmbeddings(
            model_name=current_config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
    
    def get_collection(self, kb_id: int):
        """
        获取或创建指定知识库的向量集合
        :param kb_id: 知识库ID
        :return: Chroma Collection对象
        """
        collection_name = f"kb_{kb_id}"
        return self.client.get_or_create_collection(name=collection_name)
    
    def add_documents(self, kb_id: int, documents: list, metadatas: list, ids: list):
        """
        向指定知识库添加文档向量
        :param kb_id: 知识库ID
        :param documents: 文档内容列表
        :param metadatas: 文档元数据列表
        :param ids: 文档ID列表
        """
        collection = self.get_collection(kb_id)
        # 生成向量嵌入
        embeddings = self.embedding.embed_documents(documents)
        # 添加到向量数据库
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
    
    def query(self, kb_id: int, query_text: str, top_k: int = 5):
        """
        在指定知识库中检索相似文档
        :param kb_id: 知识库ID
        :param query_text: 查询文本
        :param top_k: 返回结果数量
        :return: 检索结果
        """
        collection = self.get_collection(kb_id)
        
        # 检查集合是否有数据
        if collection.count() == 0:
            return {'documents': [], 'metadatas': [], 'distances': []}
        
        # 生成查询向量
        query_embedding = self.embedding.embed_query(query_text)
        
        # 执行检索
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return {
            'documents': results['documents'][0] if results['documents'] else [],
            'metadatas': results['metadatas'][0] if results['metadatas'] else [],
            'distances': results['distances'][0] if results['distances'] else []
        }
    
    def delete_documents(self, kb_id: int, ids: list):
        """
        从指定知识库删除文档
        :param kb_id: 知识库ID
        :param ids: 要删除的文档ID列表
        """
        collection = self.get_collection(kb_id)
        collection.delete(ids=ids)
    
    def delete_collection(self, kb_id: int):
        """
        删除指定知识库的向量集合
        :param kb_id: 知识库ID
        """
        collection_name = f"kb_{kb_id}"
        try:
            self.client.delete_collection(name=collection_name)
        except Exception:
            pass
    
    def get_collection_count(self, kb_id: int) -> int:
        """
        获取指定知识库的文档数量
        :param kb_id: 知识库ID
        :return: 文档数量
        """
        try:
            collection = self.client.get_collection(name=f"kb_{kb_id}")
            return collection.count()
        except Exception:
            return 0

# 创建全局实例
chroma_manager = ChromaManager()
