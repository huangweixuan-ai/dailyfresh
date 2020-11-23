from django.conf.urls import url
from df_goods import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^list(\d+)_(\d+)_(\d+)/$', views.goods_list,name="glist"),
    url(r'^(\d+)/$', views.goods_detail),
]

