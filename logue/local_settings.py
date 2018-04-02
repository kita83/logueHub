import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = ')guakondc1$6r#)io(rg_czr1a&bs8+q4vw9=q63@yx^s*x5z#'
DB_PASSWORD = 'vGqRxkCEiQ4qQUsD4c'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'logue_db',
        'USER': 'admin002',
        'PASSWORD': DB_PASSWORD,
        'HOST': '',
        'PORT': '',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

DEBUG = True
