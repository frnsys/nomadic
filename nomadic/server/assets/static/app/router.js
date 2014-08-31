define([
    'backbone',

    'modules/note',
    'modules/notebook'

], function(Backbone, Note, Notebook) {
    'use strict';

    var Router = Backbone.Router.extend({
        initialize: function() {
            this.note = new Note.Model(),
            this.notebook = new Notebook.Model();

            this.noteView = new Note.Views.Single({
                el: $('.note'),
                model: this.note
            });

            this.notebookView = new Notebook.Views.Single({
                el: $('.notes'),
                model: this.notebook
            });

            this.bind_interface();
        },


        bind_interface: function() {
            $('.js-show-notebooks, .js-show-notes').on('click', function() {
                $('.selected-nav').removeClass('selected-nav');
                $(this).addClass('selected-nav');
            });

            $('.js-show-notebooks').on('click', function() {
                $('.notes').hide();
                $('.notebooks').show();
            });

            $('.js-show-notes').on('click', function() {
                $('.notes').show();
                $('.notebooks').hide();
            });

            $('.notebooks').on('click', 'a', function() {
                $('.js-show-notes').click();
            });
        },


        routes: {
            '': 'get_notebook',
            '*path/': 'get_notebook',
            '*path': 'get_note'
        },


        get_notebook: function(path) {
            var self = this;

            self.fetch(path, function(data) {
                self.notebook
                    .set({
                        name: data.name,
                        url: data.url
                    })
                    .get('notes').reset(data.notes);

                self.get_note(data.notes[0].url);
            });
        },


        get_note: function(path) {
            var self = this;

            self.fetch(path, function(data) {
                self.note.set({
                    title: data.title,
                    html: data.html,
                    nburl: data.nburl
                });

                if (self.notebook.get('name') === undefined) {
                    self.get_notebook(data.nburl);
                }
            });
        },


        fetch: function(path, handler) {
            path = path || '';

            $.ajax({
                url: '/n/' + path,
                type: 'GET',
                success: function(data) {
                    handler(data);

                }, error: function(xhr, status, err) {
                    alert('Error: ' + status);
                }
            });
        }
    });

    return Router;
});
