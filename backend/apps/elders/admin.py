from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import User, Elder

UserModel = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'role', 'is_active', 'date_joined']
    search_fields = ['username', 'name']
    list_filter = ['role', 'is_active']


class ElderAdminForm(forms.ModelForm):
    """老人后台表单：可设置登录密码（老人端用户名=身份证号）"""
    login_password = forms.CharField(
        label='登录密码',
        required=False,
        min_length=6,
        max_length=128,
        widget=forms.PasswordInput(attrs={'placeholder': '留空则不创建/修改账号，填则老人可用身份证号+此密码登录'}),
        help_text='老人端登录用户名=身份证号，密码即此处设置。默认可填 123',
    )

    class Meta:
        model = Elder
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=commit)
        password = self.cleaned_data.get('login_password', '').strip()
        if password and instance.id_card:
            user, _ = UserModel.objects.get_or_create(
                username=instance.id_card,
                defaults={
                    'name': instance.name,
                    'phone': instance.phone or '',
                    'role': 'elder',
                    'elder_profile': instance,
                },
            )
            if user.elder_profile_id != instance.id:
                user.elder_profile = instance
                user.name = instance.name
                user.phone = instance.phone or ''
                user.save(update_fields=['elder_profile_id', 'name', 'phone'])
            user.set_password(password)
            user.save()
        return instance


@admin.register(Elder)
class ElderAdmin(admin.ModelAdmin):
    form = ElderAdminForm
    list_display = ['name', 'gender', 'birth_date', 'community', 'phone', 'id_card', 'is_active']
    search_fields = ['name', 'id_card', 'phone']
    list_filter = ['community', 'gender', 'is_active']
    raw_id_fields = ['community']
