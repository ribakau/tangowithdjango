from django.conf.urls import patterns, url
from rango import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^add_category/$', views.add_category, name='add_category'),
    url(r'^user/(?P<username>[\w\-]+)/$', views.user, name='user'),
    url(r'^users/$', views.user_list, name='users'),
    url(r'^edit_profile/$', views.edit_profile, name='edit_profile'),
    url(r'^password_change/$', views.password_change, name='password_change'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
    url(r'^restricted/$', views.restricted, name='restricted'),
    url(r'^goto/$', views.track_url, name='goto'))