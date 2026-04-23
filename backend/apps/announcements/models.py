from django.db import models


class Announcement(models.Model):
    CATEGORY_CHOICES = (
        ('activity', '活动'),
        ('service', '服务'),
        ('notice', '提醒'),
        ('policy', '政策'),
    )
    AUDIENCE_CHOICES = (
        ('all', '全部老人'),
        ('senior', '高龄老人'),
        ('chronic', '慢病老人'),
        ('family', '家属可见'),
    )

    title = models.CharField('标题', max_length=80)
    summary = models.CharField('摘要', max_length=160, blank=True, default='')
    content = models.TextField('正文')
    category = models.CharField('分类', max_length=20, choices=CATEGORY_CHOICES, default='notice')
    audience = models.CharField('发布对象', max_length=20, choices=AUDIENCE_CHOICES, default='all')
    cover_image = models.ImageField('封面图', upload_to='announcements/', blank=True, null=True)
    is_pinned = models.BooleanField('置顶', default=False)
    is_active = models.BooleanField('生效中', default=True)
    publish_at = models.DateTimeField('发布时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'announcement'
        verbose_name = '公告'
        verbose_name_plural = verbose_name
        ordering = ['-is_pinned', '-publish_at', '-created_at']

    def __str__(self):
        return self.title
