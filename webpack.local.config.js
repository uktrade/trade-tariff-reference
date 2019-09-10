var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')

var config = require('./webpack.base.config.js')

// Extend local webpack config here
config.mode = 'none';

config.output = {
  path: path.resolve(__dirname, './assets/tariff/bundles/'),
  filename: "[name]-[hash].js",
};

module.exports = config