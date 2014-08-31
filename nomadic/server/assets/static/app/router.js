define([
    'backbone',

    'modules/note',
    'modules/notebook'

], function(Backbone, Note, Notebook) {
    'use strict';

    var Router = Backbone.Router.extend({
        initialize: function() {
            var note = new Note.Model(),
                notebook = new Notebook.Model(),
                notebooks = new Notebook.Collection();

            this.noteView = new Note.Views.Single({
                el: $('.note'),
                model: note
            });

            this.notebookView = new Notebook.Views.Single({
                el: $('.notes'),
                model: notebook
            });

            this.notebooksView = new Notebook.Views.List({
                el: $('.notebooks'),
                collection: notebooks
            });

            $('.js-show-notebooks').on('click', function() {
                $('.notes').hide();
                $('.notebooks').show();
            });
            $('.js-show-notes').on('click', function() {
                $('.notes').show();
                $('.notebooks').hide();
            });
        },


        routes: {
            '*path(/)': 'fetch'
        },

        fetch: function(path) {
            var self = this;
            path = path || '';

            // Catch and fix up trailing slashes.
            if (path[path.length - 1] === '/')
                path = path.replace(/\/$/, "");
                self.navigate(path, {replace:true});

            $.ajax({
                url: '/n/' + path,
                type: 'GET',
                success: function(data) {
                    if (data.type === 'note') {
                        self.noteView.model.set({
                            title: data.title,
                            html: data.html
                        });

                    } else if (data.type === 'notebook') {
                        self.notebookView.model
                            .set({ name: data.name })
                            .get('notes').reset(data.notes);

                        self.notebooksView.collection.reset(data.notebooks);

                        // Fetch the notebook's first note.
                        self.fetch(data.notes[0].url);
                    }

                }, error: function(xhr, status, err) {
                    alert('Error: ' + status);
                }
            });
        }
    });

    return Router;
});
