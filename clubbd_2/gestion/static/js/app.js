
/*
var booksController = App.BooksController.create();
var arr = [];

jQuery.getJSON("../rest/v1/books/all", function(json) {
console.log(json);
});

*/

var App = Ember.Application.create({
    Book: Ember.Object.extend(),
    BooksController: Ember.Controller.extend(),
    BooksView: Ember.View.extend({
	templateName: 'books'
    }),
    ApplicationController: Ember.Controller.extend(),
    ApplicationView: Ember.View.extend({
	templateName: 'application'
    }),
    Router: Ember.Router.extend({
	BooksController: Ember.ArrayController.extend(),
	BooksView: Ember.View.extend({
	    templateName: 'books'
	}),
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
		    router.get('applicationController').connectOutlet({name:'books', context: {books: [{titre: "lol", cote: "111"}, {titre: "plop", cote: "112"}]}});
		}
	    }),
	    book: Ember.Route.extend({
		route: '/books/:book_id'
	    })
	})
    })    
});

App.initialize();
