const path = require('path');

module.exports = {
  entry: './engine/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
    library: 'CogniMapVisualizer',
    libraryTarget: 'umd',
    libraryExport: 'default',
    globalObject: 'this'
  },
  resolve: {
    extensions: ['.js', '.json'],
    fallback: {
      "fs": false,
      "path": false
    }
  },
  performance: {
    hints: false,
    maxAssetSize: 1000000,
    maxEntrypointSize: 1000000
  },
  devtool: 'source-map'
};