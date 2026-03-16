import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.community.models import Community
from apps.elders.models import Elder
from apps.health.models import DailyHealth
from apps.checkup.models import Checkup
from apps.alerts.models import Alert

User = get_user_model()

COMMUNITIES = [
    ('阳光花园社区', '市中心大道128号', '王主任', '13800001111'),
    ('翠湖名苑社区', '滨湖路56号', '李主任', '13800002222'),
    ('锦绣家园社区', '东风路88号', '张主任', '13800003333'),
    ('和谐小区社区', '文化街19号', '刘主任', '13800004444'),
]

ELDER_NAMES = [
    ('张福', 'M'), ('李秀兰', 'F'), ('王建国', 'M'), ('赵桂芳', 'F'),
    ('陈大爷', 'M'), ('孙奶奶', 'F'), ('周老', 'M'), ('吴阿姨', 'F'),
]


class Command(BaseCommand):
    help = '生成社区养老演示数据'

    def handle(self, *args, **options):
        self.stdout.write('=== 开始生成社区养老数据 ===')

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                name='系统管理员',
                role='admin',
            )
            self.stdout.write('  管理员账号创建完成 (admin / admin123)')

        communities = []
        for name, addr, person, phone in COMMUNITIES:
            c, _ = Community.objects.get_or_create(
                name=name, defaults={
                    'address': addr, 'contact_person': person, 'contact_phone': phone,
                    'description': f'{name}，辖区内老年人社区养老管理服务',
                }
            )
            communities.append(c)
        self.stdout.write(f'  {len(communities)} 个社区创建完成')

        elders = []
        for i, (name, gender) in enumerate(ELDER_NAMES):
            community = communities[i % len(communities)]
            birth_year = random.randint(1935, 1960)
            id_card = f'3301{random.randint(1, 30):02d}{birth_year}{random.randint(1, 12):02d}{random.randint(1, 28):02d}{random.randint(1000, 9999)}'
            elder, created = Elder.objects.get_or_create(
                name=name, community=community,
                defaults={
                    'gender': gender,
                    'birth_date': date(birth_year, random.randint(1, 12), random.randint(1, 28)),
                    'id_card': id_card,
                    'phone': f'138{random.randint(10000000, 99999999)}',
                    'address': f'{community.address}附近{random.randint(1, 20)}栋{random.randint(101, 2505)}',
                    'emergency_contact': f'{name[0]}家属',
                    'emergency_phone': f'139{random.randint(10000000, 99999999)}',
                    'medical_history': random.choice(['高血压', '糖尿病', '冠心病', '无', '关节炎', '高血压、糖尿病']),
                }
            )
            elders.append(elder)

            # 确保该老人有登录账号：用户名=身份证号，密码=123（每次 seed 都同步）
            user, _ = User.objects.get_or_create(
                username=elder.id_card,
                defaults={
                    'name': elder.name, 'phone': elder.phone,
                    'role': 'elder', 'elder_profile': elder,
                }
            )
            if user.elder_profile_id != elder.id:
                user.elder_profile = elder
                user.name = name
                user.phone = elder.phone
                user.save(update_fields=['elder_profile_id', 'name', 'phone'])
            user.set_password('123')
            user.save()

        self.stdout.write(f'  {len(elders)} 位老人创建完成')

        today = date.today()
        for elder in elders:
            for day_offset in range(14):
                d = today - timedelta(days=day_offset)
                is_anomaly = random.random() < 0.1
                hr = random.randint(55, 100) if not is_anomaly else random.choice([random.randint(38, 48), random.randint(125, 160)])
                bo = round(random.uniform(94, 100), 1) if not is_anomaly else round(random.uniform(82, 89), 1)
                sbp = random.randint(100, 150) if not is_anomaly else random.randint(165, 200)
                dbp = random.randint(60, 90)
                temp = round(random.uniform(36.0, 37.2), 1) if not is_anomaly else round(random.uniform(37.8, 39.0), 1)
                bs = round(random.uniform(4.0, 6.5), 1) if not is_anomaly else round(random.uniform(7.5, 12.0), 1)

                if day_offset == 0 and random.random() < 0.2:
                    continue

                DailyHealth.objects.get_or_create(
                    elder=elder, date=d,
                    defaults={
                        'heart_rate': hr, 'blood_oxygen': Decimal(str(bo)),
                        'systolic_bp': sbp, 'diastolic_bp': dbp,
                        'temperature': Decimal(str(temp)),
                        'blood_sugar': Decimal(str(bs)),
                        'weight': Decimal(str(round(random.uniform(45, 80), 1))),
                        'feeling': random.choice(['感觉良好', '有点累', '正常', '睡眠不太好', '今天不错']),
                    }
                )
        self.stdout.write('  14天健康数据生成完成')

        year = today.year
        month = today.month
        # 体检记录：前4位老人只做1次（保证体检管理「未完成」列表有数据），后4位随机
        for i, elder in enumerate(elders):
            do_first = (i < 4) or random.random() < 0.5
            do_second = (i >= 4) and random.random() < 0.4
            if do_first:
                m1 = max(1, min(month - 1, 5)) if month > 1 else 3
                Checkup.objects.get_or_create(
                    elder=elder, year=year, sequence=1,
                    defaults={
                        'check_date': date(year, m1 or 3, random.randint(1, 28)),
                        'hospital': random.choice(['市中心医院', '社区卫生服务中心', '人民医院']),
                        'height': Decimal(str(random.randint(150, 178))),
                        'weight': Decimal(str(round(random.uniform(48, 80), 1))),
                        'systolic_bp': random.randint(110, 150),
                        'diastolic_bp': random.randint(65, 95),
                        'heart_rate': random.randint(60, 90),
                        'blood_sugar': Decimal(str(round(random.uniform(4.5, 7.0), 1))),
                        'overall_result': random.choice(['基本正常', '高血压需关注', '血糖偏高建议复查', '各项指标正常']),
                        'doctor_advice': random.choice(['注意饮食清淡', '按时服药，定期复查', '加强锻炼', '无特殊建议']),
                    }
                )
            if do_second:
                m2 = 9 if month >= 9 else 11
                Checkup.objects.get_or_create(
                    elder=elder, year=year, sequence=2,
                    defaults={
                        'check_date': date(year, m2, random.randint(1, 28)),
                        'hospital': '社区卫生服务中心',
                        'height': Decimal(str(random.randint(150, 178))),
                        'weight': Decimal(str(round(random.uniform(48, 80), 1))),
                        'systolic_bp': random.randint(110, 150),
                        'diastolic_bp': random.randint(65, 95),
                        'heart_rate': random.randint(60, 90),
                        'overall_result': '基本正常',
                        'doctor_advice': '继续保持',
                    }
                )
        self.stdout.write('  体检记录生成完成')

        for elder in elders:
            done = elder.checkups.filter(year=year).count()
            if done < 2:
                Alert.objects.get_or_create(
                    elder=elder, alert_type='checkup_missing',
                    title=f'{elder.name} {year}年体检未完成',
                    defaults={
                        'level': 'warning',
                        'detail': f'今年应体检2次，目前仅完成{done}次',
                    }
                )

        for elder in elders:
            today_health = DailyHealth.objects.filter(elder=elder, date=today).first()
            if today_health and today_health.has_anomaly:
                Alert.objects.get_or_create(
                    elder=elder, alert_type='health',
                    title=f'{elder.name} 今日健康数据异常',
                    defaults={
                        'level': 'critical',
                        'detail': f'异常项: {", ".join(today_health.has_anomaly)}',
                    }
                )
        self.stdout.write('  预警数据生成完成')
        self.stdout.write(self.style.SUCCESS('=== 数据生成完成！==='))
