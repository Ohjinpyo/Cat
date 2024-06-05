const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
    app.use(
        '/api',
        createProxyMiddleware({
            target: 'http://3.38.101.95:8080',
            changeOrigin: true,
        })
    );
};

