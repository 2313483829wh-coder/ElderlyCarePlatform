# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.elders.models import Elder

User = get_user_model()


class Command(BaseCommand):
    help = '按老人姓名重置登录密码（用户名=身份证号，如：python manage.py reset_elder_password 赵桂芳 123）'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='老人姓名，如 赵桂芳')
        parser.add_argument('password', type=str, default='123', nargs='?', help='新密码，默认 123')

    def handle(self, *args, **options):
        name = (options['name'] or '').strip()
        password = (options['password'] or '123').strip()
        if not name:
            self.stderr.write('请提供老人姓名')
            return
        elder = Elder.objects.filter(name=name).first()
        if not elder:
            self.stderr.write(f'未找到姓名为「{name}」的老人')
            return
        user = User.objects.filter(username=elder.id_card).first()
        if not user:
            user = User.objects.create(
                username=elder.id_card,
                name=elder.name,
                phone=elder.phone or '',
                role='elder',
                elder_profile=elder,
            )
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(
            f'已重置：{elder.name}（身份证号/用户名 {elder.id_card}）密码为「{password}」'
        ))
