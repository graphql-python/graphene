// require.ensure([], function(require) {
//   require.include('../playground/page');
// });  
var React = require('react');
class App extends React.Component {
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
module.exports = App;
