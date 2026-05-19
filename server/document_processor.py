#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档处理模块
负责解析不同格式的文档（txt, md, pdf, docx）并进行分块
"""

import os
from abc import ABC, abstractmethod
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentParser(ABC):
    """文档解析器抽象基类"""
    
    @abstractmethod
    def parse(self, file_path: str) -> str:
        """
        解析文档内容
        :param file_path: 文件路径
        :return: 解析后的文本内容
        """
        pass

class TxtParser(DocumentParser):
    """TXT文档解析器"""
    
    def parse(self, file_path: str) -> str:
        """解析TXT文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

class MarkdownParser(DocumentParser):
    """Markdown文档解析器"""
    
    def parse(self, file_path: str) -> str:
        """解析Markdown文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

class PdfParser(DocumentParser):
    """PDF文档解析器"""
    
    def parse(self, file_path: str) -> str:
        """解析PDF文件"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text
        except ImportError:
            raise Exception("PyPDF2库未安装，请安装: pip install PyPDF2")
        except Exception as e:
            raise Exception(f"PDF解析失败: {str(e)}")

class DocxParser(DocumentParser):
    """DOCX文档解析器"""
    
    def parse(self, file_path: str) -> str:
        """解析DOCX文件"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ''
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
            return text
        except ImportError:
            raise Exception("python-docx库未安装，请安装: pip install python-docx")
        except Exception as e:
            raise Exception(f"DOCX解析失败: {str(e)}")

class DocumentProcessor:
    """
    文档处理器
    负责解析文档并进行分块处理
    """
    
    # 文件类型到解析器的映射
    PARSERS = {
        'txt': TxtParser,
        'md': MarkdownParser,
        'pdf': PdfParser,
        'docx': DocxParser
    }
    
    def __init__(self):
        """初始化文档处理器"""
        # 配置文本分块器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,        # 每个块的大小（字符数）
            chunk_overlap=50,      # 块之间的重叠大小
            length_function=len,   # 长度计算函数
            separators=["\n\n", "\n", " ", ""]  # 分隔符优先级
        )
    
    def get_parser(self, file_type: str) -> DocumentParser:
        """
        获取对应文件类型的解析器
        :param file_type: 文件类型（txt/md/pdf/docx）
        :return: 文档解析器实例
        """
        parser_class = self.PARSERS.get(file_type.lower())
        if not parser_class:
            raise ValueError(f"不支持的文件类型: {file_type}")
        return parser_class()
    
    def parse_document(self, file_path: str, file_type: str) -> str:
        """
        解析文档内容
        :param file_path: 文件路径
        :param file_type: 文件类型
        :return: 解析后的文本内容
        """
        parser = self.get_parser(file_type)
        return parser.parse(file_path)
    
    def split_document(self, content: str) -> list:
        """
        将文档内容分块
        :param content: 文档内容
        :return: 分块后的文本列表
        """
        return self.text_splitter.split_text(content)
    
    def process_document(self, file_path: str, file_type: str) -> list:
        """
        完整处理文档（解析+分块）
        :param file_path: 文件路径
        :param file_type: 文件类型
        :return: 分块后的文本列表
        """
        # 解析文档
        content = self.parse_document(file_path, file_type)
        # 分块处理
        chunks = self.split_document(content)
        return chunks

# 创建全局实例
document_processor = DocumentProcessor()
