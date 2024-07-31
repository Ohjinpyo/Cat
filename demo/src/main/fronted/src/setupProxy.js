const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
    app.use(
        '/api',
        createProxyMiddleware({
            target: 'http://13.125.228.218:8080',
            changeOrigin: true,
        })
    );
};

