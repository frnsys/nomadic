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
            var self = this,
                $note_ctrl = $('[data-pane=".note"]'),
                $notes_ctrl = $('[data-pane=".notes"]');

            $('.controls li').on('click', function() {
                var cls = $(this).data('pane');

                $('.selected-nav').removeClass('selected-nav');
                $(this).addClass('selected-nav');

                $('.notebooks, .notes').hide();
                $('.note').css('z-index', 0);
                $(cls).show();
            });

            $note_ctrl.on('click', function() {
                $('.note').css('z-index', 2);
            });

            $('.notebooks').on('click', 'a', function() {
                $notes_ctrl.click();
            });

            $('input[name=query]').on('keyup', function() {
                var query = $(this).val();
                if (query.length >= 3) {
                    self.search(query);
                    $notes_ctrl.click();
                }
            });
        },


        routes: {
            '': 'get_notebook',
            '*path/': 'get_notebook',
            '*path': 'get_note'
        },


        get_notebook: function(path, load_note) {
            var self = this,
                load_note = load_note !== false;

            self.fetch(path, '/nb/', function(data) {
                self.notebook
                    .set({
                        name: data.name,
                        url: data.url
                    })
                    .get('notes').reset(data.notes);

                if (load_note)
                    self.get_note(data.notes[0].url);
            });
        },


        get_note: function(path) {
            var self = this;

            console.log(path);

            self.fetch(path, '/n/', function(data) {
                self.note.set({
                    title: data.title,
                    html: data.html,
                    path: data.path,
                    raw: data.raw
                });

                if (self.notebook.get('name') === undefined) {
                    self.get_notebook(data.nburl, false);
                }
            });
        },

        search: function(query) {
            var self = this;

            $.ajax({
                url: '/search',
                type: 'POST',
                data: {
                    query: query
                },
                success: function(data) {
                    self.notebook
                        .set({
                            name: data.name,
                            url: data.url
                        })
                        .get('notes').reset(data.notes);

                    if (data.notes.length > 0)
                        self.get_note(data.notes[0].url);
                }
            });
        },


        fetch: function(path, endpoint, handler) {
            path = path || '';

            // Undo existing encoding, then encode the whole thing.
            path = decodeURIComponent(path);
            path = encodeURIComponent(path);

            $.ajax({
                url: endpoint + path,
                type: 'GET',
                success: function(data) {
                    handler(data);

                }, error: function(xhr, status, err) {
                    alert(xhr.status.toString() + ' : ' + xhr.responseText);
                }
            });
        }
    });

    return Router;
});
