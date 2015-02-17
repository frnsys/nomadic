require.config({
    paths: {
        lodash: '../vendor/lodash/lodash.min',
        backbone: '../vendor/backbone/backbone',
        jquery: '../vendor/jquery/dist/jquery.min',
        layoutmanager: '../vendor/layoutmanager/backbone.layoutmanager',
        template: '../vendor/lodash-template-loader/loader',
        underscore: '../vendor/underscore/underscore',
        highlight: '../vendor/highlight.js/build/highlight.pack',
        socketio: '//cdnjs.cloudflare.com/ajax/libs/socket.io/0.9.16/socket.io.min',
        mathjax: '//cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'
    },
    deps: ['main'],

    lodashLoader: {
        root: '../templates/'
    },

    shim: {
        highlight: {
            exports: 'Highlight',
            init: function() {
                return hljs;
            }
        },

        mathjax: {
            exports: 'MathJax',
            init: function () {
                MathJax.Hub.Config({
                    tex2jax: {
                        inlineMath: [['::','::'], ["\\(","\\)"]],
                        processEscapes: true
                    }
                });
                MathJax.Hub.Startup.onload();
                return MathJax;
            }
        }
    }
});

