from flask import Flask

from database import db_session, init_db
from flask_graphql import GraphQL
from schema import schema

app = Flask(__name__)
app.debug = True

default_query = '''
{
  allEmployees {
    edges {
      node {
        id,
        name,
        department {
          id,
          name
        },
        role {
          id,
          name
        }
      }
    }
  }
}'''.strip()

GraphQL(app, schema=schema, default_query=default_query)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    init_db()
    app.run()
