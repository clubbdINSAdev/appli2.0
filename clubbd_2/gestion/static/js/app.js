var __user = {};

var App = Ember.Application.create({
    __self: this,
    user: {},
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
    UserController: Em.ObjectController.extend(),
    UserView: Em.View.extend({
	templateName: 'user'
    }),
    UsersController: Ember.ArrayController.extend(),
    UsersView: Ember.View.extend({
	templateName: 'users'
    }),
    ApplicationController: Ember.Controller.extend(),
    ApplicationView: Ember.View.extend({
	templateName: 'application',
    }),
    Router: Ember.Router.extend({
	enableLogging: true,
	root: Ember.Route.extend({
	    shout: function () {
		window.alert("More information ! NOT !");
	    },
	    index: Ember.Route.extend({
		route: '/',
		connectOutlets: function(router) {
		    router.get('applicationController').connectOutlet('main', 'home');
		    router.get('applicationController').connectOutlet('login', 'loginForm');
		}
	    }),
	    /* logged: Em.Route.extend({
		index: Ember.Route.extend({
		    connectOutlets: function(router) {
			router.get('applicationController').connectOutlet('login', 'loginTrue', {name: __user.prenom, surname: __user.nom});
		    }
		})
	    }), */
	    books: Ember.Route.extend({
		showBook: Ember.Route.transitionTo('books.book'),
		route: '/books',
		index: Ember.Route.extend({
		    enter: function () {
			console.log("Entered books state.");
		    },
		    route: '/',
		    connectOutlets: function(router) {
			router.get('applicationController').connectOutlet('main', 'books', App.Book.all());
		    },
		}),
		book: Ember.Route.extend({
		    back: Ember.Route.transitionTo('root.books.index'),
		    route: '/:id',
		    enter: function () {
			console.log("Entered book state.");
		    },
		    deserialize: function(router, context){
			return App.Book.find(context.cote);
		    },
		    serialize: function(router, context){
			return {
			    id: context.cote
			}
		    },
		    connectOutlets: function(router, aBook){
			router.get('applicationController').connectOutlet('main', 'book', aBook); 
		    }
		})
	    }),
	    users: Ember.Route.extend({
		showUser: Ember.Route.transitionTo('users.user'),
		route: '/users',
		index: Ember.Route.extend({
		    route: '/',
		    connectOutlets: function(router) {
			router.get('applicationController').connectOutlet('main', 'users', App.User.all());
		    },
		}),
		user: Ember.Route.extend({
		    back: Ember.Route.transitionTo('root.users.index'),
		    route: '/:id',
		    deserialize: function(router, context){
			return App.User.find(context.id);
		    },
		    serialize: function(router, context){
			return {
			    id: context.id
			}
		    },
		    connectOutlets: function(router, user){
			router.get('applicationController').connectOutlet('main', 'user', user); 
		    }
		})
	    })
	})
    })
});


App.LoginTrueController = Em.Controller.extend(),
App.LoginTrueView = Em.View.extend({
    templateName: 'loginTrue'
});

App.LoginFormController = Em.Controller.extend(),
App.LoginFormView = Em.View.extend({
    templateName: 'loginForm',
    submit: function () {
	form = $('#login');
	login(form.children('input[type=text]').val(), form.children('input[type=password]').val(), function (json) {
	    console.log("got key");
	    __user = json;
	    
	    if (json.api_key) {
		console.log('goto root.logged.index')
		App.router.transitionTo('root.logged.index');
	    }
	    // TODO: Get cookie
	});
    }
});

App.Book = Ember.Object.extend();
App.Book.reopenClass({
    __listOfBooks: Em.A(),
    all: function () {
	var allBooks = this.__listOfBooks;
	jQuery.getJSON('/rest/v1/books/all?limit=50', function(json) {
	    console.log("Got json, " + json.length + " books");
	    allBooks.clear();
	    allBooks.pushObjects(json);
	});
	return this.__listOfBooks;
    },
    find: function (id) {
	return this.__listOfBooks.findProperty('cote', id);
    }
});

App.User = Ember.Object.extend();
App.User.reopenClass({
    __listOfUsers: Em.A(),
    all: function () {
	var allUsers = this.__listOfUsers;
	
	if (__user.api_key) {
	    var url = '/rest/v1/users/all?login='+__user.mail+
		'&api_key='+__user.api_key;
	    jQuery.getJSON(url, function(json) {
		console.log(json);
		allUsers.clear();
		allUsers.pushObjects(json);
	    });
	} 
	return this.__listOfUsers;
    },
    find: function (id) {
	return this.__listOfUsers.findProperty('id', id);
    }
});


App.initialize();
