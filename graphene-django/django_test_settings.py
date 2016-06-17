SECRET_KEY = 1

INSTALLED_APPS = [
    'graphene_django',
    'graphene_django.tests',
    'examples.starwars',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django_test.sqlite',
    }
}
