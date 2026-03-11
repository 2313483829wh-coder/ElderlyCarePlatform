from django.db import models


class Community(models.Model):
    name = models.CharField('社区名称', max_length=128, unique=True)
    address = models.CharField('地址', max_length=255)
    contact_person = models.CharField('负责人', max_length=64)
    contact_phone = models.CharField('联系电话', max_length=20)
    description = models.TextField('简介', blank=True, default='')
    is_active = models.BooleanField('在用', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '社区'
        verbose_name_plural = verbose_name
        db_table = 'community'

    def __str__(self):
        return self.name
