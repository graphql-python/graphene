import React from 'react';
import ReactDOM from 'react-dom';
import { RouteHandler, Link, State } from 'react-router';
import CodeMirror from 'codemirror';
import { graphql } from 'graphql';
import GraphiQL from 'graphiql';
import schema from './schema';

import 'codemirror/mode/python/python';
import '../css/playground.styl';

var baseCode = `import graphene

class Query(graphene.ObjectType):
    hello = graphene.String()
    ping = graphene.String(to=graphene.String())

    def resolve_hello(self, args, info):
        return 'World'

    def resolve_ping(self, args, info):
        return 'Pinging {}'.format(args.get('to'))

schema = graphene.Schema(query=Query)
`;

// function graphQLFetcher(graphQLParams) {
//   return fetch('http://swapi.graphene-python.org/graphql', {
//     method: 'post',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify(graphQLParams),
//   }).then(response => response.json());
// }
function graphQLFetcher(graphQLParams) {
  return graphql(schema, graphQLParams.query);
}
// var schema = null;

class Playground extends React.Component {
  componentDidMount() {
    this.editor = CodeMirror(ReactDOM.findDOMNode(this.refs.schemaCode), {
      value: baseCode,
      mode:  "python",
      lineNumbers: true,
      tabSize: 4,
    });
    this.markLine(6)
  }
  markLine(lineNo) {
    var mark = this.editor.markText({line: lineNo, ch: 0}, {line: lineNo, ch: 30}, {className: "called-function"});
    setTimeout(() => {
        mark.clear();
    }, 2000);
  }
  render() {
    return (
      <div className="playground">
        <div className="playground-schema" ref="schemaCode"/>
        <div className="playground-graphiql">
            <GraphiQL ref="graphiql" fetcher={graphQLFetcher} schema={schema} />
        </div>
      </div>
    );
  }
}

module.exports = Playground;
