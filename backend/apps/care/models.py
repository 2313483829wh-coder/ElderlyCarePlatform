from django.db import models


class FamilyContact(models.Model):
    RELATION_CHOICES = (
        ('child', '子女'),
        ('spouse', '配偶'),
        ('sibling', '兄弟姐妹'),
        ('relative', '亲属'),
        ('neighbor', '邻居'),
        ('other', '其他'),
    )

    elder = models.ForeignKey('elders.Elder', on_delete=models.CASCADE, related_name='family_contacts', verbose_name='老人')
    name = models.CharField('姓名', max_length=64)
    relation = models.CharField('关系', max_length=20, choices=RELATION_CHOICES, default='child')
    phone = models.CharField('联系电话', max_length=20)
    is_primary = models.BooleanField('主要联系人', default=False)
    notes = models.CharField('备注', max_length=160, blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'care_family_contact'
        verbose_name = '家属联系人'
        verbose_name_plural = verbose_name
        ordering = ['-is_primary', 'id']

    def __str__(self):
        return f'{self.elder.name}-{self.name}'


class MedicationPlan(models.Model):
    elder = models.ForeignKey('elders.Elder', on_delete=models.CASCADE, related_name='medication_plans', verbose_name='老人')
    medicine_name = models.CharField('药品名称', max_length=80)
    dosage = models.CharField('剂量', max_length=64, blank=True, default='')
    frequency = models.CharField('频次', max_length=64, blank=True, default='')
    schedule_time = models.CharField('提醒时间', max_length=64, blank=True, default='')
    instructions = models.TextField('服药说明', blank=True, default='')
    start_date = models.DateField('开始日期', null=True, blank=True)
    end_date = models.DateField('结束日期', null=True, blank=True)
    is_active = models.BooleanField('启用', default=True)
    last_taken_at = models.DateTimeField('最近确认服药时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'care_medication_plan'
        verbose_name = '用药计划'
        verbose_name_plural = verbose_name
        ordering = ['-is_active', 'medicine_name', 'id']

    def __str__(self):
        return f'{self.elder.name}-{self.medicine_name}'


class CommunityActivity(models.Model):
    title = models.CharField('活动名称', max_length=80)
    summary = models.CharField('活动摘要', max_length=160, blank=True, default='')
    content = models.TextField('活动介绍', blank=True, default='')
    location = models.CharField('活动地点', max_length=128, blank=True, default='')
    starts_at = models.DateTimeField('开始时间')
    ends_at = models.DateTimeField('结束时间', null=True, blank=True)
    max_participants = models.PositiveIntegerField('人数上限', default=30)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'care_activity'
        verbose_name = '社区活动'
        verbose_name_plural = verbose_name
        ordering = ['-starts_at', '-id']

    def __str__(self):
        return self.title


class ActivityRegistration(models.Model):
    STATUS_CHOICES = (
        ('registered', '已报名'),
        ('cancelled', '已取消'),
    )

    activity = models.ForeignKey(CommunityActivity, on_delete=models.CASCADE, related_name='registrations', verbose_name='活动')
    elder = models.ForeignKey('elders.Elder', on_delete=models.CASCADE, related_name='activity_registrations', verbose_name='老人')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='registered')
    notes = models.CharField('备注', max_length=160, blank=True, default='')
    created_at = models.DateTimeField('报名时间', auto_now_add=True)

    class Meta:
        db_table = 'care_activity_registration'
        verbose_name = '活动报名'
        verbose_name_plural = verbose_name
        unique_together = ('activity', 'elder')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.activity.title}-{self.elder.name}'


class ServiceOrder(models.Model):
    REQUEST_TYPE_CHOICES = (
        ('service', '服务预约'),
        ('sos', '紧急求助'),
    )
    SERVICE_KIND_CHOICES = (
        ('home_visit', '上门探访'),
        ('escort', '陪诊陪护'),
        ('meal', '助餐服务'),
        ('repair', '维修协助'),
        ('other', '其他需求'),
        ('emergency', '紧急求助'),
    )
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    URGENCY_CHOICES = (
        ('normal', '普通'),
        ('high', '加急'),
        ('critical', '紧急'),
    )

    elder = models.ForeignKey('elders.Elder', on_delete=models.CASCADE, related_name='service_orders', verbose_name='老人')
    community = models.ForeignKey('community.Community', on_delete=models.CASCADE, related_name='service_orders', verbose_name='社区')
    request_type = models.CharField('请求类型', max_length=20, choices=REQUEST_TYPE_CHOICES, default='service')
    service_kind = models.CharField('服务类型', max_length=20, choices=SERVICE_KIND_CHOICES, default='other')
    title = models.CharField('标题', max_length=80)
    description = models.TextField('需求说明', blank=True, default='')
    preferred_time = models.CharField('期望时间', max_length=80, blank=True, default='')
    contact_phone = models.CharField('联系电话', max_length=20, blank=True, default='')
    urgency = models.CharField('紧急程度', max_length=20, choices=URGENCY_CHOICES, default='normal')
    status = models.CharField('处理状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    response_note = models.TextField('处理反馈', blank=True, default='')
    handled_by = models.CharField('处理人', max_length=64, blank=True, default='')
    resolved_at = models.DateTimeField('完成时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'care_service_order'
        verbose_name = '服务工单'
        verbose_name_plural = verbose_name
        ordering = ['status', '-created_at']

    def __str__(self):
        return f'{self.elder.name}-{self.title}'
