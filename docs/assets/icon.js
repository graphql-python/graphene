import React from 'react';

export default class Icon extends React.Component {
    render() {
        return <span {...this.props} src={null} dangerouslySetInnerHTML={{__html:this.props.src}} />
    }
}
