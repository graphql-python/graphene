SECRET_KEY = 1

INSTALLED_APPS = [
    'graphene.contrib.django',
    'examples.starwars_django',
    'tests.contrib_django',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tests/django.sqlite',
    }
}
