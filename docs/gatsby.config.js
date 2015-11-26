var nib = require("nib");
var jeet = require("jeet");
var rupture = require("rupture");
var path = require("path");
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = function(config, env) {
  var IS_STATIC = env === 'static';
  config.merge({
     stylus: {
        use: [nib(), jeet(), rupture()]
    },
    resolveLoader: {
      root: path.join(__dirname, "node_modules"),
      modulesDirectories: ['./'],
      alias: {
        'copy': 'file-loader?name=[path][name].[ext]&context=./static',
      }
    },
    resolve: {
      root: path.join(__dirname, "node_modules"),
      alias: {
        'original-react': path.join(__dirname, "node_modules", "react"),
        'react/lib': path.join(__dirname, "node_modules", "react", "lib"),
        'react': path.join(__dirname, 'patched-react.js')
      },
      modulesDirectories: ['./']
    }
  });
  if (IS_STATIC) {
    config.plugin('extract-css', ExtractTextPlugin, ["app.css"]);
  }
  config.plugin('static', CopyWebpackPlugin, [[{ from: '../static'}]]);

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
  config.removeLoader('png');
  config.loader('png', function(cfg) {
    cfg.test = /\.png$/;
    cfg.loader = 'url-loader'
    return cfg
  })
  return config;
};
