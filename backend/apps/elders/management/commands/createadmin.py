"""创建或重置管理员账号，用于部署后首次登录。"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = '创建/重置管理员账号 (admin / admin123)'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='用户名')
        parser.add_argument('--password', default='admin123', help='密码')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': 'admin@example.com',
                'name': '系统管理员',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        if not created:
            user.email = 'admin@example.com'
            user.name = '系统管理员'
            user.role = 'admin'
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
        user.set_password(password)
        user.save()
        if created:
            self.stdout.write(self.style.SUCCESS(f'管理员已创建：{username} / {password}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'管理员密码已重置：{username} / {password}'))
        self.stdout.write('请用上述账号登录管理端。')
