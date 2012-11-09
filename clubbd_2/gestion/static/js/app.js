
/*
var booksController = App.BooksController.create();
var arr = [];
*/

var App = Ember.Application.create({
    BooksController: Ember.ArrayController.extend(),
    BooksView: Ember.View.extend({
	templateName: 'books'
    }),
    ApplicationController: Ember.Controller.extend(),
    ApplicationView: Ember.View.extend({
	templateName: 'application'
    }),
    Router: Ember.Router.extend({
	root: Ember.Route.extend({
	    index: Ember.Route.extend({
		route: '/',
		shout: function () {
		    window.alert("More information ! NOT !");
		}//,
		//redirectsTo: 'books'
	    }),
	    books: Ember.Route.extend({
		route: '/books',
		connectOutlets: function(router) {
		    router.get('applicationController').connectOutlet('books', App.Book.all());
		}
	    }),
	    book: Ember.Route.extend({
		route: '/books/:book_id'
	    })
	})
    })    
});

App.Book = Ember.Object.extend();
App.Book.reopenClass({
    __listOfBooks: Em.A(),
    all: function () {
	var allBooks = this.__listOfBooks;
	jQuery.getJSON('../rest/v1/books/all', function(json) {
	    console.log("Got json");
	    allBooks.clear();
	    console.log(allBooks.length);
	    allBooks.pushObjects(json);
	    console.log(allBooks.length);
	});
	return this.__listOfBooks;
    },
    find: function (id) {
    }
});

App.initialize();
