import React from 'react';
import ReactDOM from 'react-dom';
import { RouteHandler, Link, State } from 'react-router';
import CodeMirror from 'codemirror';
import { graphql } from 'graphql';
import GraphiQL from 'graphiql';
import schema from './schema';
import pypyjs_vm from 'pypyjs';

import 'codemirror/mode/python/python';
import 'codemirror/addon/lint/lint';
import '../css/playground.styl';

if (typeof PUBLIC_PATH === "undefined") {
  var PUBLIC_PATH = '';
}

pypyjs_vm.rootURL = `${PUBLIC_PATH}/playground/lib/`;
pypyjs_vm.cacheKey = 'graphene';

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

CodeMirror.registerHelper('lint', 'python', function (text, options, editor) {
  return (options.errors || []).map((error) => {
    var tokens = editor.getLineTokens(error.line - 1);
    tokens = tokens.filter((token, pos) => {
      return !!token.type || token.string.trim().length > 0;
    });
    if (!tokens) return [];
    return {
      message: `${error.name}: ${error.message}`,
      severity: 'error',
      type: 'syntax',
      from: CodeMirror.Pos(error.line - 1, tokens[0].start),
      to: CodeMirror.Pos(error.line - 1, tokens[tokens.length-1].end),
    };
  });
});

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

function syntaxError() {
  var marker = document.createElement("div");
  marker.style.color = "#822";
  marker.innerHTML = "●";
  return marker;
}

var default_interpreter;
class Playground extends React.Component {
  constructor() {
    super();
    this.state = {pypyjs: false, stdout: '', response:''};
  }
  stdout() {
    console.log('stdout', arguments);
  }
  componentDidMount() {
    if (default_interpreter) {
      this.pypy_interpreter = default_interpreter;
      this.pypy_interpreter.stdout = this.stdout.bind(this);
    }
    else {
      this.pypy_interpreter = new pypyjs_vm({
        stdin: function(){},
        stdout: this.stdout.bind(this),
        stderr: function(){},
        rootURL: `${PUBLIC_PATH}/playground/lib/`
      });
      default_interpreter = this.pypy_interpreter;
    }

    this.pypyjs = this.pypy_interpreter.ready().then(() => {
      return this.pypy_interpreter.exec(`
import graphene
import js
from collections import OrderedDict
from graphql.core.execution.executor import Executor
from graphql.core.execution.middlewares.sync import SynchronousExecutionMiddleware
from graphql.core.error import GraphQLError, format_error

def get_wrapped(f):
    if hasattr(f, 'func_closure') and f.func_closure:
        return get_wrapped(f.func_closure[0].cell_contents)
    return f

class TrackResolver(SynchronousExecutionMiddleware):
    @staticmethod
    def run_resolve_fn(resolver, original_resolver):
        if resolver.func.__module__ == '__main__':
            line = get_wrapped(resolver.func).resolver.func_code.co_firstlineno
            js.globals.markLine(line-3)
        return SynchronousExecutionMiddleware.run_resolve_fn(resolver, original_resolver)

__graphene_executor = Executor([TrackResolver()], map_type=OrderedDict)
`);
    }).then(() => {
      this.createSchema(baseCode);
    }).then(() => {
      this.setState({pypyjs: true, response:'"Execute the query for see the results"'});
    });

    window.markLine = (lineNo) => {
      this.markLine(lineNo);
    }

    this.editor = CodeMirror(ReactDOM.findDOMNode(this.refs.schemaCode), {
      value: baseCode,
      mode:  "python",
      theme: "graphene",
      lineNumbers: true,
      tabSize: 4,
      indentUnit: 4,
      gutters: ["CodeMirror-linenumbers", "breakpoints"],
      lint: {
        errors: [],
      },
    });
    this.editor.on("change", this.onEditorChange.bind(this));
  }
  onEditorChange() {
    if (this.changeTimeout) {
      clearTimeout(this.changeTimeout);
    }
    this.changeTimeout = setTimeout(() =>
      this.updateSchema()
    , 300);
  }
  updateSchema() {
    this.createSchema(this.editor.getValue());
  }
  createSchema(code) {
    if (this.previousCode == code) return;
    console.log('createSchema');
    this.validSchema = null;
    this.pypyjs.then(() => {
      return this.pypy_interpreter.exec(`
schema = None
${code}
assert schema, 'You have to define a schema'
`)
    }).then(() => {
      console.log('NO ERRORS');
      this.removeErrors();
      this.validSchema = true;
    }, (err) => {
      this.editor.options.lint.errors = [];
      console.log('ERRORS', err);
      this.logError(err);
      this.validSchema = false;
      // this.editor.setGutterMarker(5, "breakpoints", syntaxError());
    }).then(this.updateGraphiQL.bind(this));
    this.previousCode = code;
  }
  updateGraphiQL() {
    if (this.validSchema) {
      this.refs.graphiql.state.schema = null;
      this.refs.graphiql.componentDidMount();
      this.refs.graphiql.forceUpdate();
      this.refs.graphiql.refs.docExplorer.forceUpdate();
    }
  }
  logError(error) {
    var lines = error.trace.split('\n');
    var file_errors = lines.map((errorLine) => {
      return errorLine.match(/File "<string>", line (\d+)/);
    }).filter((x) => !! x);
    if (!file_errors.length) return;
    var line = parseInt(file_errors[file_errors.length-1][1]);
    error.line = line-2;
    if (error.name == "ImportError" && error.message == "No module named django") {
      error.message = "Django is not supported yet in Playground editor";
    }
    this.editor.options.lint.errors.push(error);
    CodeMirror.signal(this.editor, 'change', this.editor);
  }
  removeErrors() {
    this.editor.options.lint.errors = [];
    CodeMirror.signal(this.editor, 'change', this.editor);
  }
  fetcher (graphQLParams) {
    if (!this.validSchema) {
      return graphQLFetcher(arguments);
    }
    return this.execute(graphQLParams.query);
  }
  execute(query) {
    // console.log('execute', query);
    return this.pypyjs.then(() => {
      var x = `
import json
result = __graphene_executor.execute(schema.schema, '''${query}''')
result_dict = {};
if result.errors:
  result_dict['errors'] = [format_error(e) for e in result.errors]
if result.data:
  result_dict['data'] = result.data
result_json = json.dumps(result_dict)
`;
      return this.pypy_interpreter.exec(x)
    }
    ).then(() =>
      this.pypy_interpreter.get(`result_json`)
    ).then((data) => {
      var json_data = JSON.parse(data);
      return json_data;
    });
  }
  markLine(lineNo) {
    console.log(lineNo);
    var hlLine = this.editor.addLineClass(lineNo, "text", "activeline");
    // var mark = this.editor.markText({line: lineNo, ch: 0}, {line: lineNo, ch: 10}, {className: "called-function"});
    setTimeout(() => {
        this.editor.removeLineClass(lineNo, "text", "activeline");
    }, 1200);
  }
  render() {
    return (
      <div className="playground">
        {!this.state.pypyjs?<div className="loading" />:null}
        <div className="playground-schema">
          <header className="playground-schema-header">
            Schema
          </header>
          <div className="playground-schema-editor" ref="schemaCode" />
        </div>
        <div className="playground-graphiql">
            <GraphiQL ref="graphiql" fetcher={this.fetcher.bind(this)} response={this.state.response} />
        </div>
      </div>
    );
  }
}

module.exports = Playground;
