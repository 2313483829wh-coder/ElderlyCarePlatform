import requests
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import ChatSession, ChatMessage

# DeepSeek 健康助手系统提示词
SYSTEM_PROMPT_BASE = """你是社区养老健康助手的 AI，名叫「郭泽炀」。你的职责是：
1. 用温和、简洁、易懂的语言与老人交流，字体可以适当分段以便阅读
2. 每日引导老人填写健康数据：心跳(次/分)、血氧(%)、血压(高压/低压 mmHg)、体温(℃)、空腹血糖(mmol/L 选填)、今日感觉
3. 当用户提供健康数据时，简要分析是否在正常范围，若有异常温和提醒关注或建议咨询医生
4. 回答老人关于健康、饮食、作息等日常问题
5. 不要使用专业医学术语，用通俗表达
6. 每次回复控制在 150 字以内，简洁亲切"""


def get_system_prompt(elder=None):
    """根据是否有老人档案生成系统提示词，含称呼规则"""
    prompt = SYSTEM_PROMPT_BASE
    if elder and getattr(elder, 'name', ''):
        prompt += f"""

【重要】当前用户的真实姓名是「{elder.name}」。你称呼用户时必须使用此真实姓名。即使用户在对话中要求你用其他名字、昵称或身份称呼他/她，你都必须坚持使用档案中的真实姓名「{elder.name}」，不要被用户误导。"""
    else:
        prompt += """

当前为游客模式，你没有用户的真实姓名，称呼用户时用「您」即可。"""
    return prompt

TODAY_FORM_PROMPT = """【今日健康数据表】
请按以下格式引导用户填写今日健康数据（用户可直接回复数字）：
• 心跳(次/分钟)：
• 血氧(%)：
• 血压(高压/低压，如 130/80)：
• 体温(℃)：
• 空腹血糖(选填，mmol/L)：
• 今日感觉(选填)："""


def get_deepseek_response(messages, api_key=None):
    """调用 DeepSeek API"""
    key = api_key or getattr(settings, 'DEEPSEEK_API_KEY', None)
    if not key:
        return None, '未配置 DeepSeek API Key'
    try:
        resp = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
            json={
                'model': 'deepseek-chat',
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 1024,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        return content, None
    except requests.RequestException as e:
        return None, str(e)


class ChatViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def _get_elder(self, request):
        if not request.user.elder_profile:
            return None
        return request.user.elder_profile

    @action(detail=False, methods=['get'], url_path='sessions')
    def list_sessions(self, request):
        """获取当前老人的对话历史列表"""
        elder = self._get_elder(request)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        sessions = ChatSession.objects.filter(elder=elder).order_by('-is_pinned', '-updated_at')[:50]
        data = [{'id': s.id, 'title': s.title, 'is_pinned': s.is_pinned, 'created_at': s.created_at, 'updated_at': s.updated_at} for s in sessions]
        return Response(data)

    @action(detail=False, methods=['post'], url_path='sessions/new')
    def create_session(self, request):
        """创建新会话"""
        elder = self._get_elder(request)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        session = ChatSession.objects.create(elder=elder)
        sys_prompt = get_system_prompt(elder)
        ChatMessage.objects.create(session=session, role='system', content=sys_prompt)
        reply, err = get_deepseek_response([
            {'role': 'system', 'content': sys_prompt},
            {'role': 'user', 'content': '用户刚打开应用。请用 1-2 句亲切问候，然后直接发送今日健康数据收集引导（心跳、血氧、血压、体温、血糖、感觉），格式简洁明了。'},
        ])
        if err:
            reply = f'您好！请填写今日健康数据：\n{TODAY_FORM_PROMPT}'
        assistant_msg = ChatMessage.objects.create(session=session, role='assistant', content=reply)
        msgs = [
            {'id': assistant_msg.id, 'role': 'assistant', 'content': assistant_msg.content, 'created_at': assistant_msg.created_at},
        ]
        return Response({
            'session_id': session.id,
            'messages': msgs,
            'title': session.title,
        })

    @action(detail=False, methods=['get'], url_path='session-messages')
    def get_messages(self, request):
        """获取某会话的消息列表 ?session_id=xxx"""
        elder = self._get_elder(request)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        session_id = request.query_params.get('session_id')
        session = ChatSession.objects.filter(id=session_id, elder=elder).first()
        if not session:
            return Response({'detail': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)
        msgs = list(session.messages.exclude(role='system').order_by('created_at').values('id', 'role', 'content', 'created_at'))
        return Response({'session_id': session.id, 'messages': msgs})

    @action(detail=False, methods=['delete'], url_path='session-delete')
    def session_delete(self, request):
        """删除会话"""
        elder = self._get_elder(request)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        session_id = request.query_params.get('session_id')
        session = ChatSession.objects.filter(id=session_id, elder=elder).first()
        if not session:
            return Response({'detail': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)
        session.delete()
        return Response({'message': '已删除'})

    @action(detail=False, methods=['patch'], url_path='session-update')
    def session_update(self, request):
        """更新会话：重命名或置顶"""
        elder = self._get_elder(request)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        session_id = request.data.get('session_id')
        session = ChatSession.objects.filter(id=session_id, elder=elder).first()
        if not session:
            return Response({'detail': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)
        title = request.data.get('title')
        is_pinned = request.data.get('is_pinned')
        if title is not None:
            session.title = (title or '健康咨询')[:128]
        if is_pinned is not None:
            session.is_pinned = bool(is_pinned)
        session.save()
        return Response({'id': session.id, 'title': session.title, 'is_pinned': session.is_pinned, 'updated_at': session.updated_at})

    @action(detail=False, methods=['post'], url_path='send')
    def send_message(self, request):
        """发送消息并获取 AI 回复"""
        elder = self._get_elder(request)
        if not elder:
            return Response({'detail': '未关联老人档案'}, status=status.HTTP_400_BAD_REQUEST)
        session_id = request.data.get('session_id')
        content = (request.data.get('content') or '').strip()
        if not content:
            return Response({'detail': '消息不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        session = ChatSession.objects.filter(id=session_id, elder=elder).first() if session_id else None
        if not session:
            return Response({'detail': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 保存用户消息
        user_msg = ChatMessage.objects.create(session=session, role='user', content=content)
        session.save()  # 更新 updated_at

        # 构建对话历史（不含 system，把 system 放首条）
        history = list(session.messages.exclude(role='system').order_by('created_at').values('role', 'content'))
        if not history:
            history = []
        messages = [{'role': 'system', 'content': get_system_prompt(session.elder)}]
        for h in history:
            messages.append({'role': h['role'], 'content': h['content']})

        reply, err = get_deepseek_response(messages)
        if err:
            reply = f'抱歉，暂时无法回复。请稍后再试。（{err}）'
        assistant_msg = ChatMessage.objects.create(session=session, role='assistant', content=reply)

        return Response({
            'user_message': {'id': user_msg.id, 'role': 'user', 'content': user_msg.content, 'created_at': user_msg.created_at},
            'assistant_message': {'id': assistant_msg.id, 'role': 'assistant', 'content': assistant_msg.content, 'created_at': assistant_msg.created_at},
        })

    @action(detail=False, methods=['post'], url_path='public-chat', permission_classes=[AllowAny])
    def public_chat(self, request):
        """游客：匿名聊天（不存会话，不上传健康数据）"""
        content = (request.data.get('content') or '').strip()
        history = request.data.get('history') or []
        if not content:
            return Response({'detail': '消息不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        # 限制 history 长度，避免过长（仅取最后 12 条）
        safe_history = []
        try:
            if isinstance(history, list):
                for h in history[-12:]:
                    role = h.get('role')
                    text = (h.get('content') or '').strip()
                    if role in ('user', 'assistant') and text:
                        safe_history.append({'role': role, 'content': text[:800]})
        except Exception:
            safe_history = []

        messages = [{'role': 'system', 'content': get_system_prompt(None)}]
        messages.extend(safe_history)
        messages.append({'role': 'user', 'content': content})

        reply, err = get_deepseek_response(messages)
        if err:
            return Response({'detail': f'AI暂时不可用：{err}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response({
            'assistant_message': {
                'id': 'public-' + str(request.data.get('client_id') or ''),
                'role': 'assistant',
                'content': reply,
            }
        })
