var __user = {};

var App = Ember.Application.create({
    __self: this,
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
    UsersView: Em.ContainerView.extend({
	currentView: Ember.View.extend({
	    templateName: 'users',	
	})
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
	    logged: Em.Route.extend({
		index: Ember.Route.extend({
		    route: '/',
		    connectOutlets: function(router) {
			router.get('applicationController').connectOutlet('login', 'loginTrue', App.Connected.current());
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
			    router.get('applicationController').connectOutlet('main', 'books', App.Book.all());
			},
		    }),
		    book: Ember.Route.extend({
			back: Ember.Route.transitionTo('books.index'),
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
		    route: '/users',
		    addUser: function () {
			console.log("Add user");
			$('#user_modal').modal({show: false});
			var new_user = $('#new_user');
		    },
		    showUser: Ember.Route.transitionTo('users.user'),
		    index: Ember.Route.extend({
			route: '/',
			connectOutlets: function(router) {
			    router.get('applicationController').connectOutlet('main', 'users', App.User.all());
			}
		    }),
		    user: Ember.Route.extend({
			back: Ember.Route.transitionTo('users.index'),
			enter: function () {
			    console.log("user");
			    setTimeout(function () {
				$('#values').children().each(function () {
				    var id = $(this).attr('id');
				    var val = $(this).text().replace(/[\n\t]* {2}/g, '');
				    console.log(id+"- input[name="+id+"]");
				    $('#user_form_modal > fieldset').children('input[name='+id+']').val(val);
				});
				$('#user_modal').on('hidden', function () {
				    App.router.transitionTo('users.index');
				});
				$('#user_modal').modal();
			    }, 500);
			},
			route: '/:id',
			deserialize: function(router, context) {
			    return App.User.find(context.id);
			},
			serialize: function(router, context) {
			    return {
				id: context.id
			    }
			},
			connectOutlets: function(router, user) {
			    var usersController = router.get('usersController');
			    usersController.connectOutlet('user', {user: user});
			}
		    })
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
	console.log("Logging in");
	login(form.children('input[type=text]').val(), form.children('input[type=password]').val(), function (json) {
	    console.log("got key");
	    __user = json;
	    json.firstName = json.prenom;
	    json.lastName = json.nom;
	    App.Connected.updateCurrent(json);
	    
	    if (json.api_key) {
		console.log('goto root.logged.index')
		App.router.transitionTo('root.logged.index');
	    }
	    // TODO: Get cookie
	});
    }
});

App.Connected = Em.Object.create({
    __current: Em.Object.create({
	firstName: null,
	lastName: null,
	adresse: null,
	telephone: null,
	mail: null,
	id: null,
	api_key: null,
	fullName: function() {
	    var firstName = this.get('firstName');
	    var lastName = this.get('lastName');
	    return firstName + ' ' + lastName;
	}.property('firstName', 'lastName')
    }),
    updateCurrent: function (obj) {
	this.__current.setProperties(obj); 
    },
    current: function () {
	return this.__current;
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
	
	if (__user.api_key && this.__listOfUsers.length == 0) {
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
