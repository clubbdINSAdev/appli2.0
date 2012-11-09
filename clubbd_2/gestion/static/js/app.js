var App = Ember.Application.create({
    enableLogging: true,
    HomeView: Em.View.extend({
	templateName: 'home'
    }),
    HomeController: Em.Controller.extend(),
    BookController: Em.ObjectController.extend(),
    BookView: Em.View.extend({
	templateName: 'book'
    }),
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
	    shout: function () {
		    window.alert("More information ! NOT !");
	    },
	    index: Ember.Route.extend({
		route: '/',
		connectOutlets: function(router) {
	    router.get('applicationController').connectOutlet('home');
		}
	    }),
	    books: Ember.Route.extend({
		showBook: Ember.Route.transitionTo('books.book'),
		route: '/books',
		index: Ember.Route.extend({
		    enter: function () {
			console.log("Entered books state.");
		    },
		    route: '/',
		    connectOutlets: function(router) {
			router.get('applicationController').connectOutlet('books', App.Book.all());
		    },
		}),
		book: Ember.Route.extend({
		    back: Em.Route.transitionTo('root.books'),
		    route: '/book/:id',
		    enter: function () {
			console.log("Entered book state.");
		    },
		    deserialize:  function(router, context){
			return App.Book.find(context.cote);
		    },
		    serialize:  function(router, context){
			return {
			    id: context.cote
			}
		    },
		    connectOutlets:  function(router, aBook){
			router.get('applicationController').connectOutlet('book', aBook); 
		    }
		})
	    })
	})
    })    
});

App.Book = Ember.Object.extend();
App.Book.reopenClass({
    __listOfBooks: Em.A(),
    all: function () {
	var allBooks = this.__listOfBooks;
	jQuery.getJSON('../rest/v1/books/all?limit=50', function(json) {
	    console.log("Got json, " + json.length + " books");
	    console.log(json);
	    allBooks.clear();
	    allBooks.pushObjects(json);
	});
	return this.__listOfBooks;
    },
    find: function (id) {
	return this.__listOfBooks.findProperty('cote', id);
    }
});

App.initialize();
