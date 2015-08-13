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
        el: $('.notes--list'),
        model: this.notebook
      });

      this.bind_interface();
    },


    bind_interface: function() {
      var self = this;

      // Search
      $('input[name=query]').on('keyup', function() {
        var query = $(this).val();

        if (query.length >= 3) {
          clearTimeout(self.search_timer);
          self.search_timer = setTimeout(function() {
            self.search(query);
          }, 1200);
        }
      });

      // Global keybindings
      $('body').on('keydown', function(e) {
        if (e.ctrlKey) {
          switch(e.keyCode) {
            case 66: // b
              e.preventDefault();
              self.show_notebooks();
              break;
            case 78: // n
              e.preventDefault();
              self.show_notes();
              break;
            case 86: // v
              e.preventDefault();
              self.show_note();
              break;
          }
        }
      });

      // Really simple live filtering
      $('input[name=notebook]').on('keyup', function() {
        var query = $(this).val();
        $('.notebooks a').each(function() {
          var notebook = $(this).text();
          if (notebook.indexOf(query) > -1) {
            $(this).parent().show();
          } else {
            $(this).parent().hide();
          }
        });
      });

      // Go to first filtered notebook on form submit
      $('form[name=notebook]').on('submit', function(e) {
        e.preventDefault();
        $('.notebooks a:visible:first').click();
        $(this).find('input').val('');
        return false;
      });

      $('.js-notebooks').on('click', this.show_notebooks);
      $('.js-notes').on('click', this.show_notes);
      $('.js-note').on('click', this.show_note);
    },

    show_notebooks: function() {
      $('.notebooks').show();
      $('.notes, .note').hide();
      $('.notebooks input').focus();
    },
    show_notes: function() {
      $('.notes').show();
      $('.notebooks, .note').hide();
      $('.notes input').focus();
    },
    show_note: function() {
      $('.note').show();
      $('.notebooks, .notes').hide();
    },

    routes: {
      '': 'get_notebook',
      '*path/': 'get_notebook',
      '*path': 'get_note'
    },

    get_note: function(path) {
      this.load_note(path, this.show_note);
      this.set_breadcrumb(path);
    },

    get_notebook: function(path) {
      this.load_notebook(path, true, this.show_notes);
      this.set_breadcrumb(path);
    },

    load_notebook: function(path, load_note, cb) {
      var self = this,
          load_note = load_note !== false;

      self.fetch(path, '/nb/', function(data) {
        self.notebook
          .set({
            name: data.name,
            url: data.url
          })
          .get('notes').reset(data.notes);

        if (data.notes.length === 0) {
          $('.notes ul, .note').html('No notes here :)');

        } else if (load_note) {
          self.load_note(data.notes[0].url);
        }

        if (cb) {
          cb();
        }
      });
    },

    load_note: function(path, cb) {
      var self = this;

      self.fetch(path, '/n/', function(data) {
        self.note.set({
          title: data.title,
          html: data.html,
          path: self.encode(data.path),
          raw: data.raw
        });

        if (self.notebook.get('name') === undefined) {
          self.load_notebook(data.nburl, false);
        }

        if (cb) {
          cb();
        }
      });
    },

    search: function(query) {
      var self = this;
      $('input[name=query]').addClass('loading');

      $.ajax({
        url: '/search',
        type: 'POST',
        data: {
          query: query
        },
        success: function(data) {
          $('input[name=query]').removeClass('loading');
          self.notebook
            .set({
              name: data.name,
              url: data.url
            })
            .get('notes').reset(data.notes);

          // Display results
          self.show_notes();

          if (data.notes.length > 0)
            self.load_note(data.notes[0].url);
        }
      });
    },


    fetch: function(path, endpoint, handler) {
      path = path || '';

      path = this.encode(path);

      $.ajax({
        url: endpoint + path,
        type: 'GET',
        success: function(data) {
          handler(data);

        }, error: function(xhr, status, err) {
          alert(xhr.status.toString() + ' : ' + xhr.responseText);
        }
      });
    },


    set_breadcrumb: function(path) {
      var url = '/',
          parts = path.split('/').map(function(p) {
            // If this is a note,
            // don't add the additional trailing slash.
            if (/.md$/.test(p)) {
              url += p;
            } else {
              url += p + '/';
            }
            return '<a href="'+url+'">'+p+'</a>';
          });

      $('.breadcrumbs').html(parts.join(' › '));
    },

    encode: function(path) {
      // Undo existing encoding, then encode the whole thing.
      path = decodeURIComponent(path);
      path = encodeURIComponent(path);
      return path;
    }
  });

  return Router;
});
