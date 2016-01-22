import React from 'react';
import GraphenePlayground from './GraphenePlayground';

import _ from 'lodash';

const DEFAULT_CACHE_KEY = 'default';

function filterObject(object, callback, context) {
  if (!object) {
    return null;
  }
  var result = {};
  for (var name in object) {
    if (hasOwnProperty.call(object, name) &&
        callback.call(context, object[name], name, object)) {
      result[name] = object[name];
    }
  }
  return result;
}

class Playground extends React.Component {
  componentWillMount() {
    var sourceWasInjected = false;
    var queryParams = this.context.router.getCurrentQuery();

    var {
      cacheKey,
      noCache,
    } = queryParams;
    noCache = (noCache !== undefined) && (noCache !== 'false');
    if (noCache) {
      cacheKey = undefined;
    } else if (!cacheKey) {
      cacheKey = DEFAULT_CACHE_KEY;
    }
    this.schemaCacheKey = `rp-${cacheKey}-schema`;
    this.queryCacheKey = `rp-${cacheKey}-query`;
    this.cacheKey = cacheKey;

    var initialSchema;
    var initialQuery;
    var storedSchema = localStorage.getItem(this.schemaCacheKey);
    var storedQuery = localStorage.getItem(this.queryCacheKey);
    if (noCache) {
      // Use case #1
      // We use the noCache param to force a playground to have certain contents.
      // eg. static example apps
      initialSchema = queryParams.schema || '';
      initialQuery = queryParams.query || '';
      sourceWasInjected = true;
      queryParams = {};
    } else if (cacheKey === DEFAULT_CACHE_KEY) {
      // Use case #2
      // The user loaded the playground without a custom cache key.
      //   Allow code injection via the URL
      //   OR load code from localStorage
      //   OR prime the playground with some default 'hello world' code
      if (queryParams.schema != null) {
        initialSchema = queryParams.schema;
        sourceWasInjected = queryParams.schema !== storedSchema;
      } else if (storedSchema != null) {
        initialSchema = storedSchema;
      } else {
        initialSchema = require('!raw!./examples/hello.schema.py');
      }
      if (queryParams.query != null) {
        initialQuery = queryParams.query;
        sourceWasInjected = queryParams.query !== storedQuery;
      } else if (storedQuery != null) {
        initialQuery = storedQuery;
      } else {
        initialQuery = require('!raw!./examples/hello.graphql');
      }
      queryParams = filterObject({
        schema: queryParams.schema,
        query: queryParams.query,
      }, v => v !== undefined);
    } else if (cacheKey) {
      // Use case #3
      // Custom cache keys are useful in cases where you want to embed a playground
      // that features both custom boilerplate code AND saves the developer's
      // progress, without overwriting the default code cache. eg. a tutorial.
      if (storedSchema != null) {
        initialSchema = storedSchema;
      } else {
        initialSchema = queryParams[`schema_${cacheKey}`];
        if (initialSchema != null) {
          sourceWasInjected = true;
        }
      }
      if (storedQuery != null) {
        initialQuery = storedQuery;
      } else {
        initialQuery = queryParams[`query_${cacheKey}`];
        if (initialQuery != null) {
          sourceWasInjected = true;
        }
      }
      queryParams = {};
    }
    this.changeParams(queryParams);
    this.state = {initialSchema, initialQuery, sourceWasInjected};
    this.queryParams = queryParams;
  }
  shouldComponentUpdate() {
    return false;
  }
  changeParams(queryParams) {
    var router = this.context.router;
    var routeName = router.getCurrentPathname();
    var params = router.getCurrentParams();
    queryParams = _.mapValues(queryParams, encodeURIComponent);
    router.replaceWith(routeName, params, queryParams);
  }
  render() {
    return (<GraphenePlayground
      initialSchema={this.state.initialSchema}
      initialQuery={this.state.initialQuery}
      onEditSchema={(source) => {
        localStorage.setItem(this.schemaCacheKey, source);
        if (this.cacheKey === DEFAULT_CACHE_KEY) {
          this.queryParams.schema = source;
          if (!this.queryParams.query) {
            this.queryParams.query = this.state.initialQuery;
          }
          this.changeParams(this.queryParams);
        }
      }}
      onEditQuery={(source) => {
        localStorage.setItem(this.queryCacheKey, source);
        if (this.cacheKey === DEFAULT_CACHE_KEY) {
          this.queryParams.query = source;
          if (!this.queryParams.schema) {
            this.queryParams.schema = this.state.initialSchema;
          }
          this.changeParams(this.queryParams);
        }
      }}
    />);

  }
};


Playground.contextTypes = {
  router: React.PropTypes.func
};

module.exports = Playground;
