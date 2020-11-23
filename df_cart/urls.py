from django.conf.urls import url
from df_cart import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^add/$', views.add),
    url(r'^count/$', views.count1),
    url(r'^edit/$', views.edit),
    url(r'^remove/$', views.remove),
]
