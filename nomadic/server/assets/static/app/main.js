require(['app', 'router'], function(app, Router) {
    console.log('nomadic ready');

    app.router = new Router();

    Backbone.history.start({ pushState: true, root: app.root });

    // Relative links will be navigated
    // through the Backbone router.
    // If the link has a `data-bypass` attr,
    // or opens a new tab,
    // this special behavior will be ignored.
    // ---
    // For this application, only links to directories
    // and markdown (.md) files are handled by the router.
    var not = ':not([data-bypass]):not([target=_blank])';
    $(document).on('click', 'a[href$="/"]'+not+',a[href$=".md"]'+not, function(evt) {
        var href = {
            prop: $(this).prop('href'),
            attr: $(this).attr('href')
        };


        var root = location.protocol + '//' + location.host + app.root;

        // Check if the link is part of the site.
        if (href.prop.slice(0, root.length) === root) {
            var target = href.prop.replace(root, '');
            evt.preventDefault();
            Backbone.history.navigate(target, true);
        }
    });

});
