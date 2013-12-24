from tastypie.resources import ModelResource
from tastypie import fields
from mxtrax.models import Stat, MailDomain, MailTest, Customer, Config

class BlehResource(ModelResource):
	class Meta:
		queryset = MailDomain.objects.all()
		resource_name = 'maildomain'
		allowed_methods = ['get']

class StatResource(ModelResource):
	domain = fields.ForeignKey(BlehResource, 'domain', full=True)
	class Meta:
		queryset = Stat.objects.all()
		resource_name = 'stat'
		allowed_methods = ['get']
