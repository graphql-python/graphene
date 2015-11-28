import React from 'react';

class PlaygroundWrapper extends React.Component {
  constructor() {
    super();
    this.state = { currentComponent: null };
  }
  componentDidMount() {
    require(["playground-page"], (Playground) =>{
      this.setState({
        currentComponent: Playground
      });
    });
  }
  render() {
    var Current = this.state.currentComponent;
    return Current?<Current />:null;
  }
}

module.exports = PlaygroundWrapper;
