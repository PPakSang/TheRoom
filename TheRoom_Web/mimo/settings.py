
"""
Django settings for config project.
Generated by 'django-admin startproject' using Django 3.2.
For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from django.contrib.messages import constants as messages
from django.contrib.messages import constants as messages_constants

import storages

import json

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# BASE_DIR 경로 + secret.json
secret_file = os.path.join(BASE_DIR, "secret.json")

with open(secret_file) as f:
    secret = json.load(f)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secret['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'study',
    'storages',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mimo.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'mimo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if DEBUG == True:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default' : {
            'ENGINE': 'django.db.backends.mysql',
            #mysql db이름 (mysql 들어가서 디렉토리부분)
            'NAME': 'sys',                  
            'USER': 'theroom',                      
            'PASSWORD': secret['dbpassword'],                  
            'HOST': secret['HOST'],
            'PORT': '3306',                          
        }
    }
# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

# STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.naver.com' 		 # 메일 호스트 서버
EMAIL_PORT = '587' 			 # 서버 포트
EMAIL_HOST_USER = 'ppm5377@naver.com' 	 # 우리가 사용할 Gmail
EMAIL_HOST_PASSWORD = secret['EMAIL_HOST_PASSWORD']		 # 우리가 사용할 Gmail password
EMAIL_USE_TLS = True			 # TLS 보안 설정
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER	 # 응답 메일 관련 설정


SESSION_COOKIE_AGE = 3000  # 세션 만료 시간
SESSION_SAVE_EVERY_REQUEST = True  # 요청시마다 만료시간을 갱신할건지

MESSAGE_LEVEL = messages_constants.DEBUG
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# 로그 저장
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': '/path/to/django/debug.log',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }


# S3 설정을 위한 변수
# AWS_xxx 의 변수들은 aws-S3, boto3 모듈을 위한 변수들이다.

# 엑세스 키와 시크릿 키는 다른 파일로 작성, 임포트하여 사용
AWS_ACCESS_KEY_ID = secret["AWS_ID"]
AWS_SECRET_ACCESS_KEY = secret["AWS_SECRET_KEY"]

AWS_REGION = 'ap-northeast-2'
AWS_STORAGE_BUCKET_NAME = 'elasticbeanstalk-ap-northeast-2-926096212919'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (
    AWS_STORAGE_BUCKET_NAME, AWS_REGION)
AWS_DEFAULT_ACL = 'public-read'
AWS_LOCATION = 'static/admin'
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
MEDIA_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, 'media')
DEFAULT_FILE_STORAGE = 'mimo.storage.S3DefaultStorage'
STATICFILES_STORAGE = 'mimo.storage.S3StaticStorage'
