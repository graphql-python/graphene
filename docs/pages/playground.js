import React from 'react';
import DocumentTitle from 'react-document-title';
import PlaygroundWrapper from 'playground-wrapper';

class Playground extends React.Component {
  render() {
    return <DocumentTitle title="Playground - Graphene">
      <PlaygroundWrapper />
    </DocumentTitle>;
  }
}

module.exports = Playground;
