import React from 'react';
import DocumentTitle from 'react-document-title';

export default class Html extends React.Component {
  render() {
    var title = this.props.title || DocumentTitle.rewind();
    return (
      <html lang={this.props.lang} manifest="/graphene.appcache">
        <head>
          <meta charSet="utf-8"/>
          <meta httpEquiv="X-UA-Compatible" content="IE=edge"/>
          <meta name='viewport' content='width=device-width, initial-scale=1.0 maximum-scale=1.0'/>
          <title>{title}</title>
          <link rel="shortcut icon" href="/favicon.png"/>
          <link href='https://fonts.googleapis.com/css?family=Raleway:400,600,200,100' rel='stylesheet' type='text/css' />
          <link href='/app.css' rel='stylesheet' type='text/css' />
        </head>
        <body>
          <div id="react-mount" dangerouslySetInnerHTML={{__html: this.props.body}} />
          <script src="/bundle.js"/>
        </body>
      </html>
    );
  }
}
