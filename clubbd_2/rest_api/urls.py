from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^users/name/(?P<name>\w+)', 'rest_api.views.search_users_by_name'),
                       url(r'^users/all$', 'rest_api.views.get_users'),
                       url(r'^users/(?P<id>\d+)', 'rest_api.views.get_users_by_id'),
                       url(r'^books/all', 'rest_api.views.get_ouvrages')
              )
