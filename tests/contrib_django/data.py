from datetime import date

from .models import Reporter, Article

r = Reporter(first_name='John', last_name='Smith', email='john@example.com')
r.save()

r2 = Reporter(first_name='Paul', last_name='Jones', email='paul@example.com')
r2.save()

a = Article(id=None, headline="This is a test", pub_date=date(2005, 7, 27), reporter=r)
a.save()

new_article = r.articles.create(headline="John's second story", pub_date=date(2005, 7, 29))

new_article2 = Article(headline="Paul's story", pub_date=date(2006, 1, 17))
r.articles.add(new_article2)
