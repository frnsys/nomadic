define([
    'backbone',

    'modules/note',

    'template!notebook',
    'template!notebooks'
], function(Backbone, Note, notebook_tpl, notebooks_tpl) {
    'use strict';

    var Notebook = {
        Views: {}
    };


    Notebook.Model = Backbone.Model.extend({
        defaults: {
            name: '',
            notes: new Note.Collection()
        }
    });


    Notebook.Collection = Backbone.Collection.extend({
        model: Notebook.Model
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


    Notebook.Views.List = Backbone.View.extend({
        initialize: function(options) {
            this.collection = options.collection;
            this.listenTo(this.collection, 'reset', this.render);
        },

        render: function() {
            var data = this.collection.toJSON(),
                html = notebooks_tpl({notebooks: data});
            this.$el.html(html);
        }
    });


    return Notebook;
});
