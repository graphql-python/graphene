var nib = require("nib");
var jeet = require("jeet");
var ExtractTextPlugin = require("extract-text-webpack-plugin");

module.exports = function(config, env) {
  var IS_STATIC = env === 'static';
  config.merge({
     stylus: {
        use: [nib(), jeet()]
    }
  });
  if (IS_STATIC) {
    config.plugin('extract-css', ExtractTextPlugin, ["app.css"]);
  }
  config.loader('stylus', function(cfg) {
    cfg.test = /\.styl$/;
    if (IS_STATIC) {
      cfg.loader = ExtractTextPlugin.extract('style-loader', 'css-loader!stylus-loader', { allChunks: true });
    }
    else {
      cfg.loader = 'style-loader!css-loader!stylus-loader';
    }
    return cfg
  });
  return config;
};
