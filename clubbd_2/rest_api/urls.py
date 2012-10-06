from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^users/name=(?P<name>\w+)', 'rest_api.views.search_user_by_name'),
                       url(r'^users/all$', 'rest_api.views.get_users'),
                       url(r'^users/(?P<id>\d+)', 'rest_api.views.get_user_by_id'),
                       url(r'^editors/name/(?P<name>\w+)', 'rest_api.views.search_editors_by_name'),
                       url(r'^editors/all$', 'rest_api.views.get_editors'),
                       url(r'^categories/name/(?P<name>\w+)', 'rest_api.views.search_categories_by_name'),
                       url(r'^categories/all$', 'rest_api.views.get_categories'),
                       url(r'^categories/(?P<prefix>\d+)', 'rest_api.views.get_categories_by_prefix'),
                       url(r'^series/name/(?P<name>\w+)', 'rest_api.views.search_series_by_name'),
                       url(r'^series/all$', 'rest_api.views.get_series'),
                       url(r'^series/categorie/(?P<categorie_id>\d+)', 'rest_api.views.search_series_by_categorie')
              )
