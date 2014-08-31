define([
    'backbone',

    'modules/note',

    'template!notebook'
], function(Backbone, Note, notebook_tpl, notebooks_tpl) {
    'use strict';

    var Notebook = {
        Views: {}
    };


    Notebook.Model = Backbone.Model.extend({
        defaults: {
            url: '',
            name: undefined,
            notes: new Note.Collection()
        }
    });


    Notebook.Views.Single = Backbone.View.extend({
        initialize: function() {
            this.listenTo(this.model, 'change', this.render);
            this.notesView = new Note.Views.List({
                collection: this.model.get('notes')
            })
        },

        render: function() {
            var data = this.model.toJSON(),
                html = notebook_tpl(data);

            this.$el.html(html);
            this.notesView.setElement(this.$el.find('ul'));
        }
    });

    return Notebook;
});
