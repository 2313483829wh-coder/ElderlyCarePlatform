from django.db import models
from apps.elders.models import Elder


class ChatSession(models.Model):
    """老人与 AI 的对话会话"""
    elder = models.ForeignKey(
        Elder, on_delete=models.CASCADE, related_name='chat_sessions',
        verbose_name='老人',
    )
    title = models.CharField('会话标题', max_length=128, default='健康咨询')
    is_pinned = models.BooleanField('置顶', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '对话会话'
        verbose_name_plural = verbose_name
        db_table = 'ai_chat_session'
        ordering = ['-updated_at']


class ChatMessage(models.Model):
    """对话消息"""
    ROLE_CHOICES = (
        ('system', '系统'),
        ('user', '用户'),
        ('assistant', '助手'),
    )
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name='messages',
        verbose_name='会话',
    )
    role = models.CharField('角色', max_length=16, choices=ROLE_CHOICES)
    content = models.TextField('内容')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '对话消息'
        verbose_name_plural = verbose_name
        db_table = 'ai_chat_message'
        ordering = ['created_at']
