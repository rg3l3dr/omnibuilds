"""omnibuilds URL Configuration

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
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from designer.views import *
import notifications.urls
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'subplans', SubPlanViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'userprofiles', UserProfileViewSet)
router.register(r'teamprofiles', TeamProfileViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'invites', InvitationViewSet)

urlpatterns = [
    url(r'^$', landing, name = 'landing'),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^invitations/', include('invitations.urls', namespace='invitations')),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^activity/', include('actstream.urls')),
    
    url(r'^stripe/$', stripe_webhook, name='stripe_webhook'),
    url(r'^profile/$', profile, name = 'profile'),
    url(r'^invite/$', invite, name = 'invite'),
    url(r'^notifications/$', my_notifications, name = 'my_notifications'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


