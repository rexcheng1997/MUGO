const path = require('path');
const { merge } = require('webpack-merge');
const common = require('./webpack.common');

module.exports = merge(common, {
    mode: 'development',
    devtool: 'inline-source-map',
    devServer: {
        contentBase: path.resolve(__dirname, 'static'),
        watchContentBase: true,
        publicPath: '/js',
        compress: true,
        port: 3000,
        watchOptions: {
            aggregateTime: 500,
            poll: 2000,
            ignored: /node_modules/
        }
    }
});
