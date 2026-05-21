"""
对话历史模型
对应数据库表 t_chat_history
"""
from models import db
from datetime import datetime
import json


class ChatHistory(db.Model):
    """对话历史表ORM模型"""

    __tablename__ = 't_chat_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='记录ID')
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.id'), nullable=False, comment='用户ID')
    kb_id = db.Column(db.Integer, db.ForeignKey('t_knowledge_base.id'), nullable=False, comment='知识库ID')
    session_id = db.Column(db.String(64), nullable=False, comment='会话ID')
    question = db.Column(db.Text, nullable=False, comment='用户提问')
    answer = db.Column(db.Text, nullable=False, comment='AI回答')
    source_docs = db.Column(db.Text, default=None, comment='参考文档来源（JSON格式）')
    retrieved_docs = db.Column(db.Text, default=None, comment='检索到的文档详情（JSON格式）')
    prompt_text = db.Column(db.Text, default=None, comment='实际发送给LLM的完整Prompt')
    response_time_ms = db.Column(db.Integer, default=None, comment='响应时间（毫秒）')
    hit_kb = db.Column(db.Boolean, default=True, comment='是否命中知识库')
    feedback = db.Column(db.String(20), default=None, comment='用户反馈: useful/useless')
    feedback_reason = db.Column(db.String(200), default=None, comment='反馈原因')
    feedback_time = db.Column(db.DateTime, default=None, comment='反馈时间')
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')

    # 关联关系
    user = db.relationship('User', backref='chat_histories', lazy=True)
    knowledge_base = db.relationship('KnowledgeBase', backref='chat_histories', lazy=True)

    def to_dict(self):
        """将模型转换为字典"""
        source_list = []
        if self.source_docs:
            try:
                source_list = json.loads(self.source_docs)
            except (json.JSONDecodeError, TypeError):
                source_list = []

        retrieved_list = []
        if self.retrieved_docs:
            try:
                retrieved_list = json.loads(self.retrieved_docs)
            except (json.JSONDecodeError, TypeError):
                retrieved_list = []

        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.nickname if self.user else '',
            'kb_id': self.kb_id,
            'kb_name': self.knowledge_base.kb_name if self.knowledge_base else '',
            'session_id': self.session_id,
            'question': self.question,
            'answer': self.answer,
            'source_docs': source_list,
            'retrieved_docs': retrieved_list,
            'prompt_text': self.prompt_text,
            'response_time_ms': self.response_time_ms,
            'hit_kb': self.hit_kb,
            'feedback': self.feedback,
            'feedback_reason': self.feedback_reason,
            'feedback_time': self.feedback_time.strftime('%Y-%m-%d %H:%M:%S') if self.feedback_time else None,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else ''
        }
