#author: Misha Ignatenko
#copyright: Citon Computer Corp
#last edit: July 18, 2013

#description: this program makes sure that object 1 exists in Config database.
#The program pulls all the config info from object 1 and runs based on it.
#The program sends an email to each object in MailDomain database that is not
#in maintenance mode and creates a MailTest object without filling out
#receivetime field. Both test ID and Subject line are UUID4.

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from mxtrax.models import Customer, MailDomain, MailTest, Config
import mailbox
import datetime
import uuid
from pytz import timezone
import dateutil.parser
import os, sys, stat

class Command(BaseCommand):
	option_list = BaseCommand.option_list + (make_option('--long', '-1', dest='long', help='Help for the long options'),)

	help = 'help text goes here'
	def handle(self, **options):
		#first, the program needs to check that all fields in object 1
		#in Config database are not empty
		if Config.objects.filter(id=1).exists():
#		if Config.objects.get(id=1).sendinguser!=None and Config.objects.get(id=1).maxreturntime!=None and Config.objects.get(id=1).alertuser!=None and Config.objects.get(id=1).mboxpath!=None and Config.objects.get(id=1).maxfailnumber!=None and Config.objects.get(id=1).maxfailpercentage!=None and Config.objects.get(id=1).maxlatenumber!=None and Config.objects.get(id=1).maxlatepercentage!=None:
			for m in MailDomain.objects.all():
				#if a maildomain is not in maintenance mode,
				#the program sends a trial email and creates
				#a mailtest object with datetime.datetime.now()
				#as sendtime. Receivetime will be obtained
				#from the mbox file after the email bounce
				#back and we run receivetests.py. UUID is put
				#into the email's subject line, so
				#MailTest.receiveheaders always contains UUID
				if m.maintmode != True:
					u_id = uuid.uuid4()
					send_mail('%s' % u_id, 'Hi %s.' % m.customer + '\nYou are customer no.%s on the list.' % m.id + '\ndate and time right now: %s' % datetime.datetime.now(), Config.objects.get(id=1).sendinguser, ['%s' % m], fail_silently=False)

					n = MailTest(
						testid='%s' % u_id,
						sendtime=datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second),
#Aug 1						sendtime=datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month, datetime.datetime.utcnow().day, datetime.datetime.utcnow().hour, datetime.datetime.utcnow().minute, datetime.datetime.utcnow().second),
#						receiveheaders='%s' % u_id,
						maildomain=m,
						incl_in_stat=False
					)
					n.save(force_insert=True)
		else:
			print 'create Config object 1 and fill out all the fields on Config object no.1!!'
