from django.db import models
import mailbox

class Customer(models.Model):
        codename = models.CharField(max_length=15, unique=False, verbose_name="Customer Code")
        friendlyname = models.CharField(max_length=200, unique=False, verbose_name="Name")
        def __unicode__(self):
                return self.friendlyname

class MailDomain(models.Model):
        domainname = models.CharField(max_length=150, unique=False, verbose_name="Mail Domain Name")
        testuser = models.CharField(max_length=128, unique=False, verbose_name="Test User Name")
        failing = models.BooleanField(default=False, verbose_name="Failing")
        maintmode = models.BooleanField(default=False, verbose_name="Maintenance Mode")
        customer = models.ForeignKey(Customer, verbose_name="Customer")
        def __unicode__(self):
		return self.testuser + '@' + self.domainname

class MailTest(models.Model):
        testid = models.CharField(max_length=36, verbose_name="Test ID")
        sendtime = models.DateTimeField('send time')
        receivetime = models.DateTimeField('receive time', blank=True, null=True)
#        receiveheaders = models.CharField(max_length=2048, null=True, verbose_name="Received Headers")
        maildomain = models.ForeignKey(MailDomain, verbose_name="Mail Domain Name")
	incl_in_stat = models.BooleanField(default=False, verbose_name="was this MailTest already processed and included in Stats?")
        def __unicode__(self):
                return 'TEST ID: ' + self.testid + ' SEND TIME: %s' % self.sendtime + ' RECEIVE TIME: %s' % self.receivetime + ' MAIL DOMAIN: %s' % self.maildomain

class Config(models.Model):
	sendinguser = models.CharField(null=True, max_length=128, unique=True, verbose_name="Inbox email address")
	maxreturntime = models.IntegerField(default=300, verbose_name="Max round trip time")
	alertuser = models.CharField(null=True, max_length=128, unique=True, verbose_name="Send alerts to")
	mboxpath = models.CharField(null=True, max_length=255, unique=True, verbose_name="Mailbox path")
	maxfailnumber = models.IntegerField(default=0, verbose_name="Max no bounce back number")
	maxfailpercentage = models.IntegerField(default=0, verbose_name="Max no bounce back %")
	maxlatenumber = models.IntegerField(default=0, verbose_name="Max late number")
	maxlatepercentage = models.IntegerField(default=0, verbose_name="Max allowed late % for each domain")
	max_sec_until_fail = models.IntegerField(default=86400, verbose_name="Max sec until fail")
	def __unicode__(self):
		return 'SENDING USER: ' + self.sendinguser + ' MAX RETURN TIME: %s-seconds' % self.maxreturntime + '. CLICK HERE FOR MORE CONFIG INFO.'
	def has_add_permission(self, request):
		return False

class Stat(models.Model):
	domain = models.ForeignKey(MailDomain, verbose_name="MailDomain")
	d = models.DateField('Date', blank=False, null=True)
	min_delivery_time = models.IntegerField(blank=True, null=True, verbose_name="Min delivery time")
	max_delivery_time = models.IntegerField(blank=True, null=True, verbose_name="Max delivery time")
	ontime_num = models.IntegerField(default=0, verbose_name="On-time num")
	late_num = models.IntegerField(default=0, verbose_name="Late num")
	fail_num = models.IntegerField(default=0, verbose_name="Failing num")
	total_num = models.IntegerField(default=0, verbose_name="Total num")
	total_delivery_time = models.IntegerField(default=0, verbose_name="Total delivery time")
	all_done = models.BooleanField(default=False, verbose_name="Stats all done for this MailDomain on the given date?")
	def __unicode__(self):
		return 'DATE: %s' % self.d + ' MAILDOMAIN: %s' % self.domain
