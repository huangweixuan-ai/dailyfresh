from django.conf.urls import url
from df_order import views

urlpatterns = [
    url(r'^$', views.index, name='order'),
    url(r'^do_order/$', views.do_order),
    url(r'^check_pay/$', views.check_pay),

]
