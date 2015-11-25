import React from 'react';
import { RouteHandler, Link, State } from 'react-router';
import _  from 'lodash';

class Template extends React.Component {
  goToPage(event) {
    var page = event.target.value;
    this.context.router.transitionTo(page);
  }
  render() {
    var docs = this.props.config.docs;
    var docs_index = _.indexBy(this.props.pages, 'path');
    return (
      <div className="docs">
        <aside className="docs-aside">
            {Object.keys(docs).map((key) => {
                let group = docs[key];
                return <div className="docs-aside-group" key={key}>
                    <h3>{group.name}</h3>
                    {group.pages.map((page) => {
                        return <Link key={page} to={page}>{docs_index[page].data.title}</Link>
                    })}
                </div>;
            })}
            <select className="docs-aside-navselect" onChange={this.goToPage.bind(this)}>
                {Object.keys(docs).map((key) => {
                    let group = docs[key];
                    return <optgroup key={key} label={group.name}>
                        {group.pages.map((page) => {
                            return <option key={page} value={page}>{docs_index[page].data.title}</option>
                        })}
                    </optgroup>;
                })}
            </select>
        </aside>
        <div className="docs-content">
            <RouteHandler {...this.props} docs={true}/>
        </div>
      </div>
    );
  }
}

Template.contextTypes = {
  router: React.PropTypes.func
};

module.exports = Template;
