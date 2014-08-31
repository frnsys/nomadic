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
        },


        routes: {
            '*path': 'handle'
        },

        handle: function(path) {
            var self = this;
            path = path || '';

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
                        var nb = self.notebookView.model;
                        nb.set({ name: data.name });
                        nb.get('notes').reset(data.notes);

                        self.notebooksView.collection.reset(data.notebooks);
                    }
                }, error: function(xhr, status, err) {
                    alert(status);
                }
            });
        }
    });

    return Router;
});
