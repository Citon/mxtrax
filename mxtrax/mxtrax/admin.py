from django.contrib import admin
from mxtrax.models import Customer
from mxtrax.models import MailDomain
from mxtrax.models import MailTest
from mxtrax.models import Config
from mxtrax.models import Stat
from django.core.mail import send_mail
import datetime
from pytz import timezone
import dateutil.parser as dparser
import uuid
import mailbox

admin.site.register(MailTest)
admin.site.register(Customer)
admin.site.register(Stat)
class ConfigAdmin(admin.ModelAdmin):
	def has_add_permission(self, request):
		#if there is more than one object in Config3, the "add"
		#button in Django will be disabled to prevent the user from
		#adding two Config objects
		if self.model.objects.count() >= 1:
			return False
		else:
			return True
admin.site.register(Config, ConfigAdmin)

#July 26---------------------------------------------------------
class MailDomainAdmin(admin.ModelAdmin):
	fields = ['domainname', 'testuser', 'failing', 'maintmode', 'customer']
	list_display = ['testuser', 'domainname']
	list_filter = ['domainname']
admin.site.register(MailDomain, MailDomainAdmin)
