const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
    app.use(
        '/api',
        createProxyMiddleware({
            target: 'http://3.35.17.231:8080',
            changeOrigin: true,
        })
    );
};

