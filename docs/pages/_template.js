import React from 'react';
import { RouteHandler, Link, State } from 'react-router';
import Icon from 'assets/icon'

import Header from './_header'
import logo from '!raw!assets/logo.svg'
import styles from '../css/main.styl'

class Template extends React.Component {
  render() {
    var path = this.props.page.path;
    var isIndex = path == '/';
    return (
      <div>
        <header className="header">
            <div className="header-wrapper">
                <Link className="header-logo" to="/">
                    <Icon src={logo} />
                    Graphene
                </Link>
                <nav className="header-nav">
                    <Link to="/docs/quickstart/">Get started</Link>
                    <Link to="/">Playground</Link>
                    <Link to="/">Docs</Link>
                    <Link to="/community/">Community</Link>
                </nav>
            </div>
            {isIndex?
            <div className="header-extended">
                <h1>
                    GraphQL in Python<br />
                    made <strong>simple</strong>
                </h1>
                <Link to="/docs/quickstart/" className="get-started">Get Started</Link>
                <Header />
            </div>:null}
        </header>
        <RouteHandler {...this.props}/>
      </div>
    );
  }
}

module.exports = Template;
