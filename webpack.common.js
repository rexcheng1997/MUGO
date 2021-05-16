const path = require('path');

module.exports = {
    entry: './src/index.js',
    output: {
        filename: 'index.bundle.js',
        path: path.resolve(__dirname, 'static/js')
    },
    resolve: {
        alias: {
            images: path.resolve('static', 'images'),
            svg: path.resolve('static', 'svg'),
            ui: path.resolve('src', 'ui-library'),
            components: path.resolve('src', 'components'),
            util: path.resolve('src', 'utilities')
        },
        fallback: {
            crypto: require.resolve('crypto-browserify'),
            stream: require.resolve('stream-browserify')
        }
    },
    module: {
        rules: [{
            test: /\.(js|jsx)$/,
            use: 'babel-loader',
            exclude: /node_modules/,
            resolve: {
                extensions: ['.js', '.jsx']
            }
        }, {
            test: /\.scss$/,
            use: ['style-loader', {
                loader: 'css-loader',
                options: { url: false }
            }, 'sass-loader']
        }, {
            test: /\.svg$/,
            use: ['@svgr/webpack']
        }]
    }
};
