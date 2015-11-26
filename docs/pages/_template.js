import React from 'react';
import { RouteHandler, Link, State } from 'react-router';
import Icon from 'assets/icon'
import {stack as Menu} from 'react-burger-menu';

import Header from './_header'
import logo from '!raw!assets/logo.svg'
import styles from '../css/main.styl'

class Template extends React.Component {
  render() {
    var path = this.props.page.path;
    var isIndex = path == '/';
    return (
      <div>
        <Menu width={200} right>
            <span><Link to="/try/">Try it out</Link></span>
            <span><Link to="/docs/quickstart/" className={path.indexOf('/docs')==0?"active":null}>Docs</Link></span>
            <span><Link to="/community/">Community</Link></span>
            <a href="https://github.com/graphql-python/graphene/">Github</a>
        </Menu>
        <header className="header">
            <div className="header-wrapper">
                <Link className="header-logo" to="/">
                    <Icon src={logo} />
                    Graphene
                </Link>
                <nav className="header-nav">
                    <Link to="/try/">Try it out</Link>
                    <Link to="/docs/quickstart/" className={path.indexOf('/docs')==0?"active":null}>Docs</Link>
                    <Link to="/community/">Community</Link>
                    <a href="https://github.com/graphql-python/graphene/">Github</a>
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
