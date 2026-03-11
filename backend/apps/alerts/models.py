from django.db import models


class Alert(models.Model):
    TYPE_CHOICES = (
        ('health', '健康异常'),
        ('checkup_missing', '体检未完成'),
    )
    LEVEL_CHOICES = (
        ('warning', '警告'),
        ('critical', '紧急'),
    )
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('resolved', '已处理'),
    )

    elder = models.ForeignKey(
        'elders.Elder', on_delete=models.CASCADE,
        related_name='alerts', verbose_name='老人',
    )
    alert_type = models.CharField('类型', max_length=32, choices=TYPE_CHOICES)
    level = models.CharField('级别', max_length=16, choices=LEVEL_CHOICES, default='warning')
    title = models.CharField('标题', max_length=255)
    detail = models.TextField('详情')
    status = models.CharField('状态', max_length=16, choices=STATUS_CHOICES, default='pending')
    resolved_at = models.DateTimeField('处理时间', null=True, blank=True)
    resolved_note = models.TextField('处理备注', blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '预警'
        verbose_name_plural = verbose_name
        db_table = 'alert'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_level_display()}] {self.title}'
