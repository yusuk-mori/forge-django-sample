"""forge_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url, handler403, handler404, handler500
from django.contrib import admin
from django.conf import settings

from home import views as forge_views

urlpatterns = [

    # Django Admin Site
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', forge_views.forge_index),

    # Home Page
    url(r'^forge-home/', forge_views.forge_home),
    url(r'^forge-home/(?P<key>.*$)', forge_views.forge_home),

    # Viewer Extension Page
    url(r'^viewer-ext/', forge_views.viewer_ext),
    url(r'^viewer-ext/(?P<key>.*$)', forge_views.viewer_ext),

    # Authentication
    url(r'^api/forge/gettoken-deprecated/', forge_views.forge_get_code_deprecated),
    url(r'^api/forge/gettoken/', forge_views.forge_3legged_redirect),
    url(r'^api/forge/callback/oauth', forge_views.forge_3legged_callback),
    url(r'^api/forge/reset/', forge_views.forge_session_reset),

    # Ajax API
    url(r'^api/forge/jstree', forge_views.foge_get_jstree),

]

handler400 = forge_views.error400
handler403 = forge_views.error403
handler404 = forge_views.error404
handler500 = forge_views.error500

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()

