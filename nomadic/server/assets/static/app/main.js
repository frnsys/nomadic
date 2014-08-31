require(['app', 'router'], function(app, Router) {
    console.log('nomadic ready');

    app.router = new Router();

    Backbone.history.start({ pushState: true, root: app.root });

    // Relative links will be navigated
    // through the Backbone router.
    // If the link has a `data-bypass` attr,
    // this special behavior will be ignored.
    $(document).on('click', 'a[href]:not([data-bypass]):not([target=_blank])', function(evt) {
        var href = {
            prop: $(this).prop('href'),
            attr: $(this).attr('href')
        };

        var root = location.protocol + '//' + location.host + app.root;

        // Check if the link is relative
        if (href.prop.slice(0, root.length) === root) {
            evt.preventDefault();
            Backbone.history.navigate(href.attr, true);
        }
    });

});
