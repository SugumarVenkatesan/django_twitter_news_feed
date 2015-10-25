from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from django_news_app import signals
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sign_up/', ('django_news_app.views.register_user'), name="signup"),
    url(r'^confirm/(?P<activation_key>\w+)/', ('django_news_app.views.register_confirm'), name="signup_confirm"),
    url(r'^$', 'django_news_app.views.login_user', name="login"),
    url(r'^logout/$', 'django_news_app.views.logout', name="logout"),
    url(r'^home/$', 'django_news_app.views.home', name="home"),
    url(r'^reset_password/$', 'django_news_app.views.reset_password', name="reset_password"),
    url(r'^reset_password_confirm/(?P<password_reset_token>\w+)/', 'django_news_app.views.reset_password_confirm', name="reset_password_confirm"),
)


urlpatterns += staticfiles_urlpatterns()