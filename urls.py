from django.conf.urls.defaults import patterns, include, url
from autoregister import autoregister
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
autoregister('mapp.main')
urlpatterns = patterns('mapp.main',
    # ============= MAIN URL ===============================
    url(r'^$', 'views.index', name='index'),
    url(r'^home/$', 'views.home', name='home'),
    url(r'^logout/$', 'views.logout_view', name='logout'),
    url(r'^movie/(?P<movie_id>.*)/$','views.movie_info',name='movie'),
    
    # =========== ADMIN URL ================================
    url(r'^admin/', include(admin.site.urls)),
)

