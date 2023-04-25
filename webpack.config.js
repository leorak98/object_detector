const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

module.exports = {
    entry: {
        app: './static/js/app.js'
    },
    output: {
        filename: 'app.min.js',
        path: __dirname + '/static/js'
    },
    optimization: {
        minimizer: [new UglifyJsPlugin()]
    }
}