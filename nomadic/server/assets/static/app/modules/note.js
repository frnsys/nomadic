define([
    'backbone',

    'template!note',
    'template!notes'
], function(Backbone, note_tpl, notes_tpl) {
    'use strict';

    var Note = {
        Views: {}
    };


    Note.Model = Backbone.Model.extend({
        defaults: {
            title: '',
            html: ''
        }
    });


    Note.Collection = Backbone.Collection.extend({
        model: Note.Model
    });


    Note.Views.Single = Backbone.View.extend({
        initialize: function() {
            this.listenTo(this.model, 'change', this.render);
        },

        render: function() {
            var data = this.model.toJSON(),
                html = note_tpl(data);
            this.$el.html(html);
        }
    });


    Note.Views.List = Backbone.View.extend({
        initialize: function(options) {
            this.collection = options.collection;
            this.listenTo(this.collection, 'reset', this.render);
        },

        render: function() {
            var data = this.collection.toJSON(),
                html = notes_tpl({notes: data});
            this.$el.html(html);
        }
    });


    return Note;
});
