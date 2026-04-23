from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=80, verbose_name='标题')),
                ('summary', models.CharField(blank=True, default='', max_length=160, verbose_name='摘要')),
                ('content', models.TextField(verbose_name='正文')),
                ('category', models.CharField(choices=[('activity', '活动'), ('service', '服务'), ('notice', '提醒'), ('policy', '政策')], default='notice', max_length=20, verbose_name='分类')),
                ('audience', models.CharField(choices=[('all', '全部老人'), ('senior', '高龄老人'), ('chronic', '慢病老人'), ('family', '家属可见')], default='all', max_length=20, verbose_name='发布对象')),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='announcements/', verbose_name='封面图')),
                ('is_pinned', models.BooleanField(default=False, verbose_name='置顶')),
                ('is_active', models.BooleanField(default=True, verbose_name='生效中')),
                ('publish_at', models.DateTimeField(blank=True, null=True, verbose_name='发布时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '公告',
                'verbose_name_plural': '公告',
                'db_table': 'announcement',
                'ordering': ['-is_pinned', '-publish_at', '-created_at'],
            },
        ),
    ]
