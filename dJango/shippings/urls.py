from django.conf.urls import url
from shippings import views


urlpatterns = [
  	url(r'^shippings/$', views.shipping_list),
	url(r'^shippings/(?P<pk>[0-9]+)/$', views.shipping_detail),
]
