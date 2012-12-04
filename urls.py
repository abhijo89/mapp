from django.conf.urls.defaults import patterns, include, url
from autoregister import autoregister
from django.conf import settings
from django.contrib import admin
from main.sitemap import *
from api.resource import *
admin.autodiscover()
autoregister('main')
autoregister('front_end')
autoregister('tracking')
autoregister('metatag')

urlpatterns = patterns('main',
    # ============= MAIN URL ===============================
    url(r'^$', 'views.index', name='index'),
    url(r'^delorie.html','views.home', name='home_test'),
    url(r'^home/$', 'views.home', name='home'),
    url(r'^fbpost/$', 'views.fbpost', name='fbpost'),
    url(r'^logout/$', 'views.logout_view', name='logout'),
    url(r'^movie/(?P<movie_id>.*)/$','views.movie_info',name='movie'),
    #===========================================================
    url(r'^cast_(?P<person_id>.*).dhtml$', 'views.person_info',name='person_info'),    
    # =========== ADMIN URL ================================
    url(r'^admin/', include(admin.site.urls)),
    (r'^tracking/', include('tracking.urls')),
    
    url(r'^api-auth/', include('djangorestframework.urls', namespace='djangorestframework')),
    url(r'^api/$', ListOrCreateModelView.as_view(resource=MyMovieResource)),
    url(r'^api/(?P<pk>[^/]+)/$', InstanceModelView.as_view(resource=MyMovieResource)),
    
)

urlpatterns += patterns('front_end',
      #TEmplate view
      url(r'^home/map/$', 'views.map_view',name='map_view'),
      url(r'^new_account$','views.register_view',name='register_view'),
      #From submit
      url(r'^register$','views.register',name='register'),
      url(r'^home/myaccount/$','views.myaccount',name='myaccount'),
      url(r'^home/profile/(?P<user_id>.*)/$', 'views.myaccount', name='user_page'),
      url(r'user/request/(?P<user_id>.*)/$', 'views.friend_request', name='friend_request'),
      url(r'user/accept/(?P<user_id>.*)/$', 'views.friend_accept', name='friend_accept'),
      url(r'^home/myaccount/edit_profile_page/$','views.edit_profile_page',name='edit_profile_page'),
      url(r'home/myaccount/edit_profile_page/delete-pic/$', 'views.delete_pic', name='delete_pic'),
      url(r'home/myaccount/edit_profile_page/profile-pic/$', 'views.profile_pic', name='profile_pic'),
      #Search
      url(r'^home/search/$','views.search_index',name='search_index'),
      url(r'^search/(?P<category>.*)/$','views.search',name='search'),
      url(r'^search/(?P<category>.*)/(?P<category_item>.*).dhtml$','views.search_movie_by_category',name='search_movie'),
      url(r'^search.dhtml','views.search_globel',name='search_globel'),
      
      #Contact Us
      url(r'^home/contact/thankyou/', 'views.thankyou',name='search_index'),
      url(r'^home/contact-us/', 'views.contactview',name='contact-us'),
      #Team MEmbers 
      url(r'^team_memder_(?P<member_id>.*).dhtml$', 'views.team_memders',name='team_memders'),
      url(r'^show/(?P<category>.*).dhtml$', 'views.show_top_movie',name='show_top_movie'),
      url(r'^show_country/(?P<category>.*).dhtml$', 'views.show_top_movie_country',name='show_top_movie_country'),
     
)


"""
urlpatterns = patterns('',
    url(r'^admin/password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    (r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
    (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
    
)
"""
urlpatterns += patterns('',
		(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
    
urlpatterns += patterns('django.contrib.staticfiles.views',
    url(r'^static/(?P<path>.*)$', 'serve'),
)


