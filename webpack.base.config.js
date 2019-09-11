const path = require("path")
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const glob = require("glob");

module.exports = {
  context: __dirname,
  entry: {
    index: './static/js/index', // entry point of our app. static/js/index.js should require other js modules and dependencies it needs
    defaultVueApp: './static/js/vue/apps/default-app',
    vueComponents:  glob.sync('./static/js/vue/components/*.js'),
  },
  output: {
      path: path.resolve(__dirname, './static/js/bundles'),
      filename: "[name]-[hash].js",
  },
  module: {
    rules: [
      { test: /\.vue$/, loader: 'vue-loader'},
      { test: /\.js?$/, exclude: /node_modules/, loader: 'babel-loader'},
      { test: /\.css$/, use: ['vue-style-loader', 'css-loader']},
    ],
  },
  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
    new VueLoaderPlugin(),
  ],
  resolve: {
    modules: ['node_modules', 'bower_components'],
    extensions: ['.js'],
    alias: {
      'vue$': 'vue/dist/vue.esm.js'
    }
  },
}