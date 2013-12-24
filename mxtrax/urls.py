from django.conf.urls import *

from tastypie.api import Api
from mxtrax.api.resources import StatResource, BlehResource
v1_api = Api(api_name='v1')
v1_api.register(StatResource())
v2_api = Api(api_name='v2')
v2_api.register(BlehResource())

from django.contrib import admin
admin.autodiscover()

from mxtrax.views import demo_linewithfocuschart


urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	url(r'^admin/', include(admin.site.urls)),
	url(r'^api/', include(v1_api.urls)),
	url(r'^api/', include(v2_api.urls)),
	url(r'^dash/$', demo_linewithfocuschart),
	url(r'^dash/(?P<mdomain>([^@]+@[^@]+\.[^@]+))/$', demo_linewithfocuschart),
)
