from django.conf.urls import patterns, url
from django.conf.urls import include
from rest_framework.urlpatterns import format_suffix_patterns
from restapp import views

urlpatterns = patterns('',
    url(r'^$', views.api_root),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^users/?$', views.UserList.as_view(), name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/?$', views.UserDetail.as_view(), name='user-detail'),
    url(r'^stores/?$', views.StoreList.as_view(), name='store-list'),
    url(r'^stores/(?P<pk>[0-9a-fA-F]+)/?$', views.StoreDetail.as_view(), name='store-detail'),
    url(r'^products/?$', views.ProductList.as_view(), name='product-list'),
    url(r'^products/(?P<pk>[0-9]+)/?$', views.ProductDetail.as_view(), name='product-detail'),
    url(r'^checkins/?$', views.CheckinList.as_view(), name='checkin-list'),
    url(r'^checkins/(?P<pk>[0-9]+)/?$', views.CheckinDetail.as_view(), name='checkin-detail'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
