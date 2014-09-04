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
            $(document).on('keydown', this.keydown.bind(this));
        },

        render: function() {
            var data = this.model.toJSON(),
                html = note_tpl(data);
            this.$el.html(html);
        },

        events: {
            'click .js-edit': 'edit',
            'click .js-save': 'save',
            'click .js-cancel': 'cancel'
        },

        keydown: function(e) {
            if (e.ctrlKey) {
                switch(e.keyCode) {
                    case 69: // e
                        e.preventDefault();
                        this.edit();
                        break;
                    case 88: // x
                        e.preventDefault();
                        this.cancel();
                        break;
                    case 83: // s
                        e.preventDefault();
                        this.save();
                        break;
                }
            }
        },

        edit: function() {
            this.$el.find('.plaintext-editor, .js-save, .js-cancel').show();
            this.$el.find('.content, .js-edit').hide();
        },

        cancel: function() {
            this.$el.find('.plaintext-editor, .js-save, .js-cancel').hide();
            this.$el.find('.content, .js-edit').show();
        },

        save: function() {
            var self = this,
                text = this.$el.find('.plaintext-editor').val();
            text = $.trim(text);

            $.ajax({
                url: '/n/' + this.model.get('path'),
                type: 'PUT',
                data: {
                    text: text
                },
                success: function(data) {
                    self.model.set(data);
                }, error: function(xhr, status, err) {
                    alert(xhr.status.toString() + ' : ' + xhr.responseText);
                }
            });
        },

        remove: function() {
            $(document).off('keydown', this.keydown);
            Backbone.View.prototype.remove.call(this);
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
