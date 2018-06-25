import os
from socket import gethostname


HOSTNAME = gethostname()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.getenv('SECRET_KEY')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'bootstrap4',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',
    'django_nose',
    'accounts',
    'feed',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
            ],
        },
    },
]

# 国際化
LANGUAGE_CODE = 'ja-JP'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

SITE_ID = 1
WSGI_APPLICATION = 'logue.wsgi.application'
ROOT_URLCONF = 'logue.urls'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/logue/'

# 継承したユーザークラス定義
AUTH_USER_MODEL = 'accounts.LogueUser'

# django-allauth でカスタムユーザーモデル使用時に username を使わない設定
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'None'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
SOCIALACCOUNT_AUTO_SIGNUP = True

if 'local' in HOSTNAME:
    from .local_settings import *
    DEBUG = True
    ALLOWED_HOSTS = ['127.0.0.1', 'testserver']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'logue_db',
            'USER': 'admin001',
            'PASSWORD': DB_PASSWORD,
            'HOST': 'localhost',
            'PORT': '5432'
        }
    }
    MEDIA_URL = '/media/'
    STATIC_URL = '/static/'
else:
    DEBUG = False
    ALLOWED_HOSTS = ['*']
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config()
    }
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # S3共通の設定
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = 'loguehub'
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # キャッシュ有効期間:1日
    }

    # 静的ファイルの設定
    AWS_LOCATION = 'static'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)

    # メディアファイルの設定
    AWS_PUBLIC_MEDIA_LOCATION = 'media'
    DEFAULT_FILE_STORAGE = 'logue.backends.PublicMediaStorage'
    # MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_PUBLIC_MEDIA_LOCATION)
    MEDIA_URL = "https://s3-ap-northeast-1.amazonaws.com/%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_PUBLIC_MEDIA_LOCATION)
    AWS_PRELOAD_METADATA = True

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# django-nose, coverage configure
TEST_APPS = (
    'feed',
    'accounts',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',  # coverage を取る
    '--cover-html',  # coverage を html で cover/ に出力する
    '--cover-package=' + ",".join(TEST_APPS),
]

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Default logging for Django. This sends an email to the site admins on every
# HTTP 500 error. Depending on DEBUG, all other log records are either sent to
# the console (DEBUG=True) or discarded (DEBUG=False) by means of the
# require_debug_true filter.
DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s a',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}
