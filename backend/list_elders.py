import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.elders.models import Elder

print('\n老人账号列表（身份证号登录，密码统一123）:')
print('=' * 60)
for e in Elder.objects.all().select_related('community'):
    print(f'{e.community.name:12} | {e.name:6} | {e.id_card}')
print('=' * 60)
