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
    __self: this
});

App.IndexRoute = Ember.Route.extend({
    enter: function () {
	console.log('Entered index route.');
    },
    redirect: function () {
	var cur = sessionStorage.getItem('current');
	if (cur) {
	    this.transitionTo('logged');
	}
    },
    renderTemplate: function() {
	this.render('home', {
	    outlet: 'main'
	});
	this.render('loginForm', {
	    outlet: 'login'
	});
    }
});

App.LoggedRoute = Em.Route.extend({
    enter: function () {
	console.log('Entered logged route.');
    },
    redirect: function () {
	var cur = sessionStorage.getItem('current');
	if (!cur) {
	    console.log('Not logged in redirecting ...');
	    App.alert('You\'re not logged in ! Log in please.');
	    this.transitionTo('index');
	}
    }
});

App.LoggedIndexRoute = Em.Route.extend({
    enter: function() {
	App.alert('You are logged in !', 'success');
    },
    renderTemplate: function () {
	this.render('loggedHome', {
	    outlet: 'main'
	});
	this.render('loginTrue', {
	    outlet: 'login'
	});
    }
});

App.LoggedBooksRoute = Ember.Route.extend({
    enter: function () {
	console.log("Entered logge.books route.");
    },
    model: function () {
	return App.Book.find();
    },
    setupController: function(controller, model) {
	controller.set('test', '1,2,3');
	controller.set('books', model);
    },
    renderTemplate: function () {
	this.render('logged/books', {
	    into: 'application',
	    outlet: 'main',
	});
    }
});

App.LoggedBookRoute = Ember.Route.extend({
    enter: function () {
	console.log("Entered book state.");
    },
    model: function(params){
	return App.Book.find(params.book_id);
    },
    renderTemplate: function () {
	this.render('logged/book', {
	    into: 'application',
	    outlet: 'main'
	});
    }
});

App.LoggedUsersRoute = Ember.Route.extend({
    enter: function () {
	console.log("Entered logged.users route.");
    },
    addUser: function () {
	console.log("Add user");
	$('#user_modal').modal({show: false});
	var new_user = $('#new_user');
    },
    model: function () {
	return  App.User.find();
    },
    renderTemplate: function () {
	this.render('logged/users', {
	    into: 'application',
	    outlet: 'main'
	});
    }
});	


App.LoggedUserRoute = Ember.Route.extend({
    enter: function () {
	console.log("user");
    },
    model: function(params) {
	return App.User.find(params.user_id);
    },
    renderTemplate: function () {
	this.render('logged/user', {
	    into: 'application',
	    outlet: 'main'
	});
    } 
});

App.LoansRoute = Em.Route.extend({
    enter: function () {
	console.log("Entered loans route.");
    },
    renderTemplate: function () {
	this.render('loans', {
	    into: 'application',
	    outlet: 'main'
	});
    } 
});

App.LoansIndexRoute = Em.Route.extend({
    enter: function () {
	console.log("Entered loans.index route.");
    }
});

App.LoansNewRoute = Em.Route.extend({
    enter: function () {
	console.log('Enter the matrix.');
    },
    setupController: function (controller, model) {
	controller.set('users', App.User.find());
	controller.set('books', App.Book.find()); 
    }
});

App.Router.map(function() {
    this.resource('logged', function() {
	this.route('books');
	this.route('book', {path: '/books/:book_id'});

	this.route('users');
	this.route('user', {path: '/users/:user_id'});
    });
    
    this.resource('loans', function () {
	this.route('new');
    });
});

App.LoansNewController = Em.Controller.extend({
    isUsersHidden: true,
    isBooksHidden: true,
    userSearch: '',
    bookSearch: '',

    _allUsers: function() {
	var _users = App.User.find();
	this.set('allUsers', _users);
	return _users;
    },

    focusUsers: function () {
	console.log('Hack the gibson.');
	this.set('isBooksHidden', true);
	this.set('isUsersHidden', false);
    },
    focusBooks: function () {
	console.log('Hack the fender.');
	this.set('isBooksHidden', false);
	this.set('isUsersHidden', true);
    },
    updateUserSearch: function () {
	var 
	userSearch = this.userSearch,
	users = this.get('allUsers') || this._allUsers(),
	filtered_users =
	    users.filter(function (i) {
		return i.get('prenom').toLowerCase().indexOf(userSearch.toLowerCase()) != -1;
	    });
	this.set('users', filtered_users);
    }.observes('userSearch'),
    updateBookSearch: function () {
	console.log('k');
	console.log(this.bookSearch);
    }.observes('bookSearch')
});

App.UserSearchField = Em.TextField.extend();

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

	login(form.children('input[type=text]').val(),
	      form.children('input[type=password]').val(), 
	      function (json) {
		  console.log("got key");
		  json.firstName = json.prenom;
		  json.lastName = json.nom;
		  App.Connected.updateCurrent(json);
		  sessionStorage.setItem('current', JSON.stringify(App.Connected.current()));
		  
		  if (json.api_key) {
		      console.log('logged')
		      App.Router.router.transitionTo('logged.index');
		  }
		  // TODO: Get cookie
	      }, function (err) {
		  console.log('login failed: '+err.reason);
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
	api_key: null
	/*fullName: function() {
	    var firstName = this.get('firstName');
	    var lastName = this.get('lastName');
	    return firstName + ' ' + lastName;
	}.property('firstName', 'lastName')*/
    }),
    updateCurrent: function (obj) {
	this.__current.setProperties(obj); 
    },
    current: function () {
	return this.__current;
    }
});

App.Book = DS.Model.extend({
    primaryKey: 'cote',
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
});

App.Book.reopenClass({
    url: function () {
	return '/books';
    },
    args: function (conf) {
	var ret = '?';
	
	if (conf.all) {
	    ret += 'limit=20';
	}	    
	return ret;
    }
});

App.User = DS.Model.extend({
    adresse: DS.attr('string'),
    mail: DS.attr('string'),
    nom: DS.attr('string'),
    prenom: DS.attr('string'),
    telephone: DS.attr('string')
});

App.User.reopenClass({
    url: function () {
	    return '/users';
    },
    args: function () {
	var user = App.Connected.current(),
	ret = '';
	
	if (user.get('api_key')) {
	    ret =  '?login='+user.get('mail')+
		'&api_key='+user.get('api_key');
	}

	return ret;
    }
});

// DS.Adapter.configure('primaryKey', {
//     book: 'cote'
// });

App.adapter = DS.Adapter.create({
    url: '/rest/v',
    version: 1,
    find: function (store, type, id) {
	var url = this.url + this.version + type.url() + '/' + id + type.args(),
	self = this;
	
	console.log(url);
	jQuery.getJSON(url, function(data) {
	    var payload = {};

	    payload[type.toString().split('.')[1].toLowerCase()] = data;
	    self.didFindRecord(store, type, payload, id);
	});
    },
    findMany: function (store, type, ids) {
	// TODO
    },
    findQuery: function (store, type, query, result) {
	console.log('findQuery');
	var url = this.url + this.version + type.url() + '/name/'+ query.firstName + type.args(),
	self = this;

	console.log(url);
	jQuery.getJSON(url, function(data) {
	    console.log(type.name);
	    var payload = {};

	    payload[type.toString().split('.')[1].toLowerCase()+'s'] = data;
	    console.log(payload);
	    self.didFindQuery(store, type, payload, result);
	});
    },
    findAll: function (store, type) {
	console.log('find all');
	var url = this.url + this.version + type.url() + '/all'+ type.args({all: true}),
	self = this;

	console.log(url);
	jQuery.getJSON(url, function(data) {
	    console.log(type.name);
	    var payload = {};

	    payload[type.toString().split('.')[1].toLowerCase()+'s'] = data;
	    self.didFindAll(store, type, payload);
	});
    },
    // Write
});

App.Store = DS.Store.extend({
    revision: 11,
    adapter: App.adapter
});

App.ready = function () {
    var cur = sessionStorage.getItem('current');
    if (cur) {    
	cur = JSON.parse(cur);
	console.log('Already logged in. (as '+cur.lastName+')')
	App.Connected.updateCurrent(cur);
    }
}

App.initialize();
