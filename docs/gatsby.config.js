var nib = require("nib");
var jeet = require("jeet");
var rupture = require("rupture");
var path = require("path");
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var webpack = require("webpack");
var CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = function(config, env) {
  var IS_STATIC = env === 'static';
  var entry = config._config.entry.slice();
  var publicPath = config._config.output.publicPath;
  // var output = config._config.output;
  // output.filename = "[name].js";
  config._config.entry = {
    bundle: entry,
  };
  config.merge({
    stylus: {
      use: [nib(), jeet(), rupture()]
    },
    output: {
      filename: "[name].js",
      publicPath: "/",
    },
    resolveLoader: {
      root: path.join(__dirname, "node_modules"),
      modulesDirectories: ['./'],
    },
    resolve: {
      root: path.join(__dirname, "node_modules"),
      alias: {
        'original-react': path.join(__dirname, "node_modules", "react"),
        'react/lib': path.join(__dirname, "node_modules", "react", "lib"),
        'react': path.join(__dirname, 'patched-react.js'),
        'pypyjs': '../playground/graphene-js/pypyjs',
        'playground-page': (env != "static")?'../playground/page':'../pages/_empty',
        'playground-wrapper': (env == "develop")?'../playground/page':'../playground/wrapper',
      },
      modulesDirectories: ['./']
    }
  });
  if (IS_STATIC) {
    config.plugin('extract-css', ExtractTextPlugin, ["app.css"]);
  }
  config.plugin('static', CopyWebpackPlugin, [[{ from: '../static'}]]);
  config.plugin('define-env', webpack.DefinePlugin, [{
    "ENV": JSON.stringify(env),
    "PUBLIC_PATH": JSON.stringify(publicPath),
  }]);
  // if (env != "static") {
  //   config.plugin('commons', webpack.optimize.CommonsChunkPlugin, ["commons.js"]);
  // }

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
