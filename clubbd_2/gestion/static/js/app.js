var __user = {};

var App = Ember.Application.create({
    alert: function (message, type, time) {
	var message = message || '',
	type = type || 'warning',
	time = time || 3000;

	var alert = $('<div>', {
	    'class': 'fade in alert alert-'+type,
	    html: message,
	    css: {
		margin: 'auto',
		'margin-bottom': '10px'
	    }
	});

	alert.prependTo('#main');

	window.setTimeout(function (){
	    alert.alert('close');
	}, time);
    },
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
		enter: function() {
		    App.alert('You are logged in !', 'success');
		},
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
		    enter: function () {
			
		    },
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
			enter: function () {
			    console.log("user");
			    $('#user_modal').modal();
			    $('#user_modal').on('hidden', function () {
				App.router.transitionTo('users.index');
			    });
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
	var div = $('#login');
	var form = div.children('form').first();
	console.log("Logging in");
	
	var loading = $('<img>', {
	    src: "../static/img/loading.png",
	    alt: "loading...",
	    css: {
		display: 'none',
		height: '30px', 
		margin: 'auto',
		'padding-top': '5px'
	    },
	    'class': 'nav pull-right'
	});

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
	}, function (err) {
	    loading.fadeToggle();
	    form.fadeToggle();
	    App.alert('Login failed ...', 'error');
	});
	
	div.append(loading);

	form.fadeToggle();
	loading.fadeToggle();
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
