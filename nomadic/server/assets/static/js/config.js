require.config({
    paths: {
        lodash: 'vendor/lodash/dist/lodash.compat',
        backbone: 'vendor/backbone/backbone',
        jquery: 'vendor/jquery/dist/jquery.min',
        layoutmanager: 'vendor/layoutmanager/backbone.layoutmanager',
        template: 'vendor/lodash-template-loader/loader',
        underscore: 'vendor/underscore/underscore'
    },
    deps: ['main'],

    lodashLoader: {
        root: 'templates/'
    }
});
