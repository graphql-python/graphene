import React from 'react';
import DocumentTitle from 'react-document-title';
import { link } from 'gatsby-helpers';

var DOCS_BASEURL = "https://github.com/graphql-python/graphene/edit/master/docs/pages/";

class Markdown extends React.Component {
  render() {
    var post = this.props.page.data;
    var pagePath = this.props.page.requirePath;
    var documentUrl = `${DOCS_BASEURL}${pagePath}`;

    return (
      <DocumentTitle title={`${post.title?post.title+' - ':''}${this.props.config.siteTitle}`}>
        <div className="markdown">
          {post.title?<div className="title">
            <h1>{post.title}</h1>
          </div>:null}
          <div className="wrapper" dangerouslySetInnerHTML={{__html: post.body}}/>
          <a href={documentUrl} className="improve-document-link">Improve this document!</a>
        </div>
      </DocumentTitle>
    );
  }
}

module.exports = Markdown;
