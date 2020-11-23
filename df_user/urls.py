from django.conf.urls import url
from df_user import views

urlpatterns = [
    url(r'^register/$', views.register, name='register'),
    url(r'^check_register/$', views.check_register),
    url(r'^user_check/$', views.user_check),
    url(r'^login/$', views.login, name='login'),
    url(r'^login_check/$', views.login_check),
    url(r'^info/$', views.info, name='info'),
    url(r'^center/$',views.center, name='center'),
    url(r'^user_site/$', views.site, name='site'),
    url(r'^shou_save/$', views.shou_save),
    url('^logout$',views.logout,name='logout'),
]
