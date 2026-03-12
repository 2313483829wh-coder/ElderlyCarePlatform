from django.db import models


class Checkup(models.Model):
    """年度体检记录，每年应完成 2 次"""
    elder = models.ForeignKey(
        'elders.Elder', on_delete=models.CASCADE,
        related_name='checkups', verbose_name='老人',
    )
    year = models.IntegerField('年度')
    sequence = models.IntegerField('第几次', help_text='1=上半年, 2=下半年')
    check_date = models.DateField('体检日期')
    hospital = models.CharField('体检机构', max_length=128, blank=True, default='')

    # 基本体检项目
    height = models.DecimalField('身高(cm)', max_digits=5, decimal_places=1, null=True, blank=True)
    weight = models.DecimalField('体重(kg)', max_digits=5, decimal_places=1, null=True, blank=True)
    systolic_bp = models.IntegerField('收缩压', null=True, blank=True)
    diastolic_bp = models.IntegerField('舒张压', null=True, blank=True)
    heart_rate = models.IntegerField('心率', null=True, blank=True)
    blood_sugar = models.DecimalField('血糖(mmol/L)', max_digits=5, decimal_places=1, null=True, blank=True)
    blood_lipid = models.CharField('血脂', max_length=64, blank=True, default='')
    liver_function = models.CharField('肝功能', max_length=128, blank=True, default='')
    kidney_function = models.CharField('肾功能', max_length=128, blank=True, default='')
    blood_routine = models.CharField('血常规', max_length=255, blank=True, default='')
    urine_routine = models.CharField('尿常规', max_length=255, blank=True, default='')
    ecg = models.CharField('心电图', max_length=128, blank=True, default='')
    chest_xray = models.CharField('胸部X光', max_length=128, blank=True, default='')
    b_ultrasound = models.CharField('B超', max_length=255, blank=True, default='')
    vision = models.CharField('视力', max_length=64, blank=True, default='')
    hearing = models.CharField('听力', max_length=64, blank=True, default='')

    overall_result = models.TextField('综合结论', blank=True, default='')
    doctor_advice = models.TextField('医生建议', blank=True, default='')
    report_file = models.FileField('体检报告', upload_to='checkup_reports/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '体检记录'
        verbose_name_plural = verbose_name
        db_table = 'checkup'
        unique_together = ['elder', 'year', 'sequence']
        ordering = ['-year', '-sequence']

    def __str__(self):
        return f'{self.elder.name} {self.year}年第{self.sequence}次体检'
