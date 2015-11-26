// React patched version for render in server side always with same ids
if (typeof window === "undefined") {
  var ServerReactRootIndex = require('react/lib/ServerReactRootIndex');
  console.log(ServerReactRootIndex);
  ServerReactRootIndex.createReactRootIndex = function(){
      return "graphene";
  };
}

module.exports = require('original-react');
