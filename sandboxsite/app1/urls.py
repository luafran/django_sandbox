from django.conf.urls import patterns, url
from app1 import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='simple'),
    url(r'^class/?$', views.MyView.as_view(), name='class'),
    url(r'^json/?$', views.JSONView.as_view(), name='json'),
    url(r'^login/?$', views.LoginView.as_view(), name='login'),
    url(r'^logout/?$', views.my_logout, name='logout'),
    url(r'^protected/?$', views.protected_view, name='protected'),
    url(r'^conditional/?$', views.conditional_view, name='conditional'),
    url(r'^cached/?$', views.cached_view, name='cached'),
)
