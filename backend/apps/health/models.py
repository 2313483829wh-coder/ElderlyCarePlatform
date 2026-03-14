from django.db import models
from django.conf import settings


class DailyHealth(models.Model):
    """老人每日上传的健康数据（一天一条）"""
    elder = models.ForeignKey(
        'elders.Elder', on_delete=models.CASCADE,
        related_name='daily_health', verbose_name='老人',
    )
    date = models.DateField('日期')
    heart_rate = models.IntegerField('平均心跳(bpm)', null=True, blank=True)
    blood_oxygen = models.DecimalField('血氧(%)', max_digits=5, decimal_places=1,
                                        null=True, blank=True)
    systolic_bp = models.IntegerField('收缩压(mmHg)', null=True, blank=True)
    diastolic_bp = models.IntegerField('舒张压(mmHg)', null=True, blank=True)
    temperature = models.DecimalField('体温(℃)', max_digits=4, decimal_places=1,
                                       null=True, blank=True)
    blood_sugar = models.DecimalField('空腹血糖(mmol/L)', max_digits=5, decimal_places=1,
                                       null=True, blank=True)
    weight = models.DecimalField('体重(kg)', max_digits=5, decimal_places=1,
                                  null=True, blank=True)
    feeling = models.CharField('今日感觉', max_length=255, blank=True, default='',
                                help_text='老人自述今天的身体感觉')
    submitted_at = models.DateTimeField('提交时间', auto_now_add=True)

    class Meta:
        verbose_name = '每日健康数据'
        verbose_name_plural = verbose_name
        db_table = 'daily_health'
        unique_together = ['elder', 'date']
        ordering = ['-date']

    def __str__(self):
        return f'{self.elder.name} {self.date}'

    def is_likely_invalid_submission(self):
        """明显不合理的录入不参与预警（乱填、测试数据）"""
        # 心率：常见乱填
        if self.heart_rate is not None and self.heart_rate in (0, 1, 999, 1000, 9999):
            return True
        if self.heart_rate is not None and self.heart_rate > 250:
            return True
        # 血氧 0% 或 100%
        if self.blood_oxygen is not None:
            bo = float(self.blood_oxygen)
            if bo == 0 or bo == 100:
                return True
        # 血压 0 或 999 等
        if self.systolic_bp is not None and self.systolic_bp in (0, 999, 1000):
            return True
        if self.diastolic_bp is not None and self.diastolic_bp in (0, 999, 1000):
            return True
        if self.systolic_bp and self.diastolic_bp and self.systolic_bp < self.diastolic_bp:
            return True
        # 体温明显超出人体范围
        if self.temperature is not None:
            tmp = float(self.temperature)
            if tmp < 35 or tmp > 42:
                return True
        # 血糖 0 或 >30
        if self.blood_sugar is not None:
            bs = float(self.blood_sugar)
            if bs == 0 or bs > 30:
                return True
        return False

    @property
    def has_anomaly(self):
        """检查是否有异常指标（基于国际医学标准）"""
        t = settings.HEALTH_THRESHOLDS
        problems = []
        
        # 心率检查
        if self.heart_rate:
            if self.heart_rate < t['heart_rate_min']:
                problems.append(f'心率过缓({self.heart_rate}bpm)')
            elif self.heart_rate > t['heart_rate_max']:
                problems.append(f'心率过速({self.heart_rate}bpm)')
        
        # 血氧检查
        if self.blood_oxygen:
            if float(self.blood_oxygen) < t['blood_oxygen_min']:
                problems.append(f'血氧偏低({self.blood_oxygen}%)')
        
        # 血压检查
        if self.systolic_bp:
            if self.systolic_bp < t['systolic_bp_min']:
                problems.append(f'收缩压过低({self.systolic_bp}mmHg)')
            elif self.systolic_bp > t['systolic_bp_max']:
                problems.append(f'收缩压过高({self.systolic_bp}mmHg)')
        
        if self.diastolic_bp:
            if self.diastolic_bp < t['diastolic_bp_min']:
                problems.append(f'舒张压过低({self.diastolic_bp}mmHg)')
            elif self.diastolic_bp > t['diastolic_bp_max']:
                problems.append(f'舒张压过高({self.diastolic_bp}mmHg)')
        
        # 体温检查
        if self.temperature:
            if float(self.temperature) < t['temperature_min']:
                problems.append(f'体温过低({self.temperature}℃)')
            elif float(self.temperature) > t['temperature_max']:
                problems.append(f'体温偏高({self.temperature}℃)')
        
        # 血糖检查
        if self.blood_sugar:
            if float(self.blood_sugar) < t['blood_sugar_min']:
                problems.append(f'血糖偏低({self.blood_sugar}mmol/L)')
            elif float(self.blood_sugar) > t['blood_sugar_max']:
                problems.append(f'血糖偏高({self.blood_sugar}mmol/L)')
        
        return problems
