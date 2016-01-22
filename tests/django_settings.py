SECRET_KEY = 1

INSTALLED_APPS = [
    'graphene.contrib.django',
    'graphene.contrib.django.tests',
    'examples.starwars_django',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tests/django.sqlite',
    }
}
