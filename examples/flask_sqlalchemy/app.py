import json
from flask import Flask
from database import db_session, init_db

from schema import schema, Department

app = Flask(__name__)


@app.route('/')
def hello_world():
    query = '{node(id:"%s"){name, employees { edges { node {name} } } } }' % Department.global_id(1)
    return json.dumps(schema.execute(query).data)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    init_db()
    app.run()
