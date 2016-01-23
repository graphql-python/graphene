from flask import Flask
from database import db_session, init_db

from schema import schema, Department
from graphql_flask import GraphQL

app = Flask(__name__)
app.debug = True

default_query = '''
{
  node(id:"%s") {
    name
    employees {
      edges {
        node {
          name
        }
      }
    }
  }
}'''.strip() % Department.global_id(1)

GraphQL(app, schema=schema, default_query=default_query)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    init_db()
    app.run()
