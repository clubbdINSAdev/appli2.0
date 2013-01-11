/*******************************************************
TODO'S:
- Move stuff into different files
********************************************************/

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
    LoggedController: Em.Controller.extend(),
    LoggedView: Em.View.extend({
	templateName: 'loggedHome'
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
		enter: function () {
		    var cur = sessionStorage.getItem('current');
		    if (cur) {
			cur = JSON.parse(cur);
			console.log('Already logged in. (as '+cur.lastName+')')
			App.Connected.updateCurrent(cur);
			App.router.transitionTo('logged.index');
		    }
		},
		connectOutlets: function(router) {
		    router.get('applicationController').connectOutlet('main', 'home');
		    router.get('applicationController').connectOutlet('login', 'loginForm');
		}
	    }),
	    logged: Em.Route.extend({
		route: '/logged',
		goToUsers: Ember.Route.transitionTo('users.index'),
		goToBooks: Ember.Route.transitionTo('books.index'),
		enter: function() {
		    App.alert('You are logged in !', 'success');
		},
		index: Ember.Route.extend({
		    route: '/',
		    enter: function () {
			console.log('Know in logged in zone.');
		    },
		    connectOutlets: function(router) {
			router.get('applicationController').connectOutlet('main', 'logged');
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
			    router.get('applicationController').connectOutlet('main', 'books', App.Book.findAll());
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
	    json.firstName = json.prenom;
	    json.lastName = json.nom;
	    App.Connected.updateCurrent(json);
	    sessionStorage.setItem('current', JSON.stringify(App.Connected.current()));
	    
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

App.Book = DS.Model.extend({
    is_manga: DS.attr('string'),
    isbn: DS.attr('string'), 
    description: DS.attr('string'),
    ean: DS.attr('string'),
    serie_id: DS.attr('number'), 
    numero: DS.attr('number'),
    cote: DS.attr('string'), 
    in_serie: DS.attr('boolean'), 
    date_entree: DS.attr('date'), 
    titre: DS.attr('string'),
    empruntable: DS.attr('boolean'),

    url: '/books' 
});


// App.Book_old.reopenClass({
//     __listOfBooks: Em.A(),
//     all: function () {
// 	var allBooks = this.__listOfBooks;
// 	jQuery.getJSON('/rest/v1/books/all?limit=50', function(json) {
// 	    console.log("Got json, " + json.length + " books");
// 	    allBooks.clear();
// 	    allBooks.pushObjects(json);
// 	});
// 	return this.__listOfBooks;
//     },
//     find: function (id) {
// 	return this.__listOfBooks.findProperty('cote', id);
//     }
// });

App.User = DS.Model.extend({
    adresse: DS.attr('string'),
    mail: DS.attr('string'),
    nom: DS.attr('string'),
    prenom: DS.attr('string'),
    telephone: DS.attr('string')
});

/*App.User_old.reopenClass({
    __listOfUsers: Em.A(),
    all: function () {
	console.log('get all users');
	var allUsers = this.__listOfUsers,
	user = App.Connected.current();
	
	if (user.get('api_key') && this.__listOfUsers.length == 0) {
	    var url = '/rest/v1/users/all?login='+user.get('mail')+
		'&api_key='+user.get('api_key');
	    console.log(url);
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
});*/


App.adapter = DS.Adapter.create({
    url: '/rest/v',
    version: 1,
    find: function (store, type, id) {
	var url = this.url + this.version + type.url + '/' + id,
	self = this;
	
	jQuery.getJSON(url, function(data) {
	    self.didFindRecord(store, type, data, id);
	});
    },
    findMany: function (store, type, ids) {
	// TODO
    },
    findQuery: function (store, type, query, result) {
	// TODO
    },
    findAll: function (store, type) {
	var url = this.url + this.version + type.url,
	self = this;
	jQuery.getJSON(url, function(data) {
	    self.didFindAll(type, data);
	});
    }
    // Write
});

App.Store = DS.Store.create({
    revision: 11,
    adapter: App.adapter
});

App.initialize();
