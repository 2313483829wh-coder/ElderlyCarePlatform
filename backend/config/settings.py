import os
import sys
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'apps'))

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-community-elderly-care-platform-2026'
)
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'
_allowed = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').strip()
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]
if '*' not in ALLOWED_HOSTS:
    for h in ('127.0.0.1', 'localhost'):
        if h not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(h)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'apps.community',
    'apps.elders',
    'apps.health',
    'apps.checkup',
    'apps.alerts',
    'apps.ai',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', str(BASE_DIR / 'db.sqlite3')),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

AUTH_USER_MODEL = 'elders.User'

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = (
    os.environ.get('CORS_ALLOW_ALL_ORIGINS', '').lower() == 'true' or DEBUG
)
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS', 'http://localhost:5173'
).split(',')

# 反向代理 + HTTPS（Nginx）下的 CSRF 配置
# 通过环境变量 DJANGO_CSRF_TRUSTED_ORIGINS 配置（逗号分隔），否则根据公网 IP 兜底
_csrf_trusted = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').strip()
if _csrf_trusted:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_trusted.split(',') if o.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [
        'https://47.111.26.171',
        'http://47.111.26.171',
    ]

# 让 Django 正确识别代理转发的 https
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# 健康数据阈值，超出则预警
# 健康预警阈值（基于WHO和国际医学标准，针对老年人群体）
HEALTH_THRESHOLDS = {
    # 心率（静息心率）
    'heart_rate_min': 60,      # 低于60 bpm可能心动过缓
    'heart_rate_max': 100,     # 高于100 bpm可能心动过速
    
    # 血氧饱和度
    'blood_oxygen_min': 95,    # 低于95%需要关注，低于90%为低氧血症
    
    # 血压（收缩压/舒张压）- 基于ACC/AHA 2017高血压指南
    'systolic_bp_min': 90,     # 收缩压低于90可能低血压
    'systolic_bp_max': 140,    # 收缩压≥140为高血压（老年人标准稍宽松）
    'diastolic_bp_min': 60,    # 舒张压低于60可能低血压
    'diastolic_bp_max': 90,    # 舒张压≥90为高血压
    
    # 体温
    'temperature_min': 36.0,   # 低于36℃可能体温过低
    'temperature_max': 37.3,   # 高于37.3℃可能发热
    
    # 空腹血糖 - 基于ADA美国糖尿病协会标准
    'blood_sugar_min': 3.9,    # 低于3.9 mmol/L为低血糖
    'blood_sugar_max': 6.1,    # 高于6.1 mmol/L为空腹血糖受损（7.0以上为糖尿病）
}

# DeepSeek API（生产环境建议用环境变量 DEEPSEEK_API_KEY）
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-6fd4968ae1e7494190e42fe2b6871edf')
