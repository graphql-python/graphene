import sys, os
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_PATH + '/examples/')

SECRET_KEY = 1

INSTALLED_APPS = [
    'graphene_django',
    'graphene_django.tests',
    'starwars',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django_test.sqlite',
    }
}
