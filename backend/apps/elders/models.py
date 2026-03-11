from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """管理员或老人账号"""
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('elder', '老人'),
    )
    role = models.CharField('角色', max_length=16, choices=ROLE_CHOICES, default='admin')
    name = models.CharField('姓名', max_length=64, blank=True, default='')
    phone = models.CharField('手机号', max_length=20, blank=True, default='')
    elder_profile = models.OneToOneField(
        'Elder', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='user_account', verbose_name='关联老人',
    )

    class Meta:
        verbose_name = '账号'
        verbose_name_plural = verbose_name
        db_table = 'sys_user'

    def __str__(self):
        return self.name or self.username


class Elder(models.Model):
    GENDER_CHOICES = (('M', '男'), ('F', '女'))
    community = models.ForeignKey(
        'community.Community', on_delete=models.CASCADE,
        related_name='elders', verbose_name='所属社区',
    )
    name = models.CharField('姓名', max_length=64)
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField('出生日期')
    id_card = models.CharField('身份证号', max_length=18, unique=True)
    phone = models.CharField('联系电话', max_length=20, blank=True, default='')
    address = models.CharField('家庭住址', max_length=255, blank=True, default='')
    emergency_contact = models.CharField('紧急联系人', max_length=64, blank=True, default='')
    emergency_phone = models.CharField('紧急联系电话', max_length=20, blank=True, default='')
    medical_history = models.TextField('既往病史', blank=True, default='')
    notes = models.TextField('备注', blank=True, default='')
    is_active = models.BooleanField('在管', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '老人'
        verbose_name_plural = verbose_name
        db_table = 'elder'
        ordering = ['community', 'name']

    def __str__(self):
        return f'{self.name}({self.community.name})'

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
