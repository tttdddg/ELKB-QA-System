"""
问答对话路由
提供RAG问答和对话历史查询接口
"""
import uuid
import json
from flask import Blueprint, request, g
from models import db
from models.chat_history import ChatHistory
from models.knowledge_base import KnowledgeBase
from models.kb_permission import KBPermission
from utils.auth import login_required
from utils.response import success, error, page_response

chat_bp = Blueprint('chat', __name__)


def _check_kb_permission(kb_id, user_id, role):
    """检查用户是否有知识库访问权限，管理员跳过检查"""
    if role == 'admin':
        return True
    return KBPermission.query.filter_by(kb_id=kb_id, user_id=user_id).first() is not None


@chat_bp.route('/ask', methods=['POST'])
@login_required
def ask():
    """
    RAG知识库问答接口
    请求参数: question, kb_id, session_id(可选), template_id(可选)
    返回: AI回答、参考来源、检索结果详情
    """
    data = request.get_json()
    if not data:
        return error('请提供问题信息')

    question = data.get('question', '').strip()
    kb_id = data.get('kb_id')
    session_id = data.get('session_id', str(uuid.uuid4().hex[:16]))
    template_id = data.get('template_id')

    if not question:
        return error('问题不能为空')
    if not kb_id:
        return error('请选择知识库')

    kb = KnowledgeBase.query.get(kb_id)
    if not kb or kb.status != 1:
        return error('知识库不存在或已禁用')

    # 权限检查
    if not _check_kb_permission(kb_id, g.user_id, g.role):
        return error('您没有访问该知识库的权限', 403)

    try:
        from services.rag_service import RAGService
        rag_service = RAGService()
        answer, source_docs, retrieved_docs, prompt_text, elapsed_ms, hit_kb = \
            rag_service.ask(question, kb_id, template_id=template_id)
    except Exception as e:
        return error(f'问答服务异常: {str(e)}')

    chat = ChatHistory(
        user_id=g.user_id,
        kb_id=kb_id,
        session_id=session_id,
        question=question,
        answer=answer,
        source_docs=json.dumps(source_docs, ensure_ascii=False),
        retrieved_docs=json.dumps(retrieved_docs, ensure_ascii=False),
        prompt_text=prompt_text,
        response_time_ms=elapsed_ms,
        hit_kb=hit_kb
    )
    db.session.add(chat)
    db.session.commit()

    return success({
        'answer': answer,
        'source_docs': source_docs,
        'retrieved_docs': retrieved_docs,
        'session_id': session_id,
        'chat_id': chat.id,
        'hit_kb': hit_kb,
        'response_time_ms': elapsed_ms
    })


@chat_bp.route('/history', methods=['GET'])
@login_required
def get_history():
    """
    获取对话历史列表（分页）
    普通用户只能查看自己的记录，管理员可查看所有
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    kb_id = request.args.get('kb_id', type=int)

    query = ChatHistory.query

    if g.role != 'admin':
        query = query.filter_by(user_id=g.user_id)

    if kb_id:
        query = query.filter_by(kb_id=kb_id)

    query = query.order_by(ChatHistory.create_time.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    items = [item.to_dict() for item in pagination.items]
    return page_response(items, pagination.total, page, page_size)


@chat_bp.route('/session/<session_id>', methods=['GET'])
@login_required
def get_session(session_id):
    """
    获取指定会话的所有对话记录
    """
    query = ChatHistory.query.filter_by(session_id=session_id)

    if g.role != 'admin':
        query = query.filter_by(user_id=g.user_id)

    chats = query.order_by(ChatHistory.create_time.asc()).all()
    return success([chat.to_dict() for chat in chats])


@chat_bp.route('/feedback/<int:chat_id>', methods=['POST'])
@login_required
def submit_feedback(chat_id):
    """
    提交回答反馈
    请求参数: feedback(useful/useless), feedback_reason(可选)
    """
    chat = ChatHistory.query.get(chat_id)
    if not chat:
        return error('对话记录不存在', 404)

    if chat.user_id != g.user_id and g.role != 'admin':
        return error('只能反馈自己的对话记录', 403)

    data = request.get_json()
    feedback = data.get('feedback', '').strip()
    if feedback not in ('useful', 'useless'):
        return error('反馈类型无效，可选: useful/useless')

    chat.feedback = feedback
    chat.feedback_reason = data.get('feedback_reason', '')[:200]
    chat.feedback_time = db.func.now()
    db.session.commit()

    return success(message='反馈已提交')
