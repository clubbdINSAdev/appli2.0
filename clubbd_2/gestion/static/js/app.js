var App = Em.Application.create();

App.MyView = Em.View.extend({
    shout: function () {
	window.alert("More information ! NOT !");
    }
});
