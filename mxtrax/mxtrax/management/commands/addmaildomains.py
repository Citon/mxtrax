#author: Misha Ignatenko
#last edit: July 18, 2013

#description: this program scans the CSV file and looks for lines that have
#4 items in 1 row separated by 3 commas. the user should type in the command
#prompt "python manage.py addmaildomains -f [absolute path of CSV database]",
# i.e. "python manage.py addmaildomains -f /root/pr/emaillist.csv" to run
#the program. the program will also count and print how many email addresses
#from CSV file were imported into MailDomains database during the most
#recent import, how many entries in CSV file were already in MailDomains
#database, and how many emails did not fit email model regular expression and
#thus were not imported into MailDomains. The program will print an error
#statement if the user doesn't specify filename and if the file does not exist.

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from mxtrax.models import Customer, MailDomain, MailTest, Config
from django.db import models
import re
from optparse import OptionParser
import sys
import csv

class Command(BaseCommand):

	option_list = BaseCommand.option_list + (make_option("-f", "--filename", action="store", type="string", dest="filename", help="LEARN HOW TO RUN THE COMMAND!"),)


	help = 'you need to specify absolute path to your customer csv file'
	def handle(self, *args, **options):
		parser = OptionParser(option_list=self.option_list)
		(option, args) = parser.parse_args()

# Check that -f <filename> is set when the user "python manage.py
#addmaildomains -f /root/pr/emaillist.csv"
		if option.filename == None:
			print self.help
			sys.exit(1)
		try:
#Aug 2			if Config.objects.get(id=1).sendinguser!=None and Config.objects.get(id=1).maxreturntime!=None and Config.objects.get(id=1).alertuser!=None and Config.objects.get(id=1).mboxpath!=None and Config.objects.get(id=1).maxfailnumber!=None and Config.objects.get(id=1).maxfailpercentage!=None and Config.objects.get(id=1).maxlatenumber!=None and Config.objects.get(id=1).maxlatepercentage!=None:
			if Config.objects.filter(id=1).exists():
				with open(option.filename, 'rb') as f:
					str = ''
					reader = csv.reader(f)
					row_count = 0
					c_already_in_md = 0
					c_newly_imported_domains = 0
					c_domains_with_errors = 0
					for row in reader:
						#this is to make sure the program doesn't count the row with "Customer.friendlyname" as an actual item in csv database
						if row[0] != "Customer.friendlyname":
							row_count += 1
						#this makes sure that 4 items are in a row. we are also excluding the first sample row
						if len(row) == 4 and row[0] != "Customer.friendlyname":
							counter = 0
							for c in Customer.objects.all():
								if c.codename == row[1] and c.friendlyname == row[0]:
									counter += 1
							if counter == 0:
								#we should only add customers that aren't already in the Customer db
								#if counter == 1, there is already a customer in Customer db that the program is trying to import from the CSV file
								n = Customer(
									codename = row[1],
									friendlyname = row[0]
								)
								n.save(force_insert=True)
							#now make sure that the exact same maildomain in not already in the system
							#if counter equals 0, then maildomain isn't in the system yet.
							#we are using the same "counter" variable to out whether each maildomain in the csv file is already in MailDomain db
							counter = 0
							for md in MailDomain.objects.all():
								if md.testuser == row[2] and md.domainname == row[3]:
									counter += 1
							strng = ''
							if counter == 0:
								strng = row[2] + '@' + row[3]

								# Define email_re - Same pattern that used to be in django.core.validators
								email_re = re.compile(
									r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
									r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
									r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$)'
									r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)

								if email_re.match(strng):
								#match the maildomain that is being created with a Customer
								#create a maildomain object and connect it to the given customer
									for cust in Customer.objects.all():
										if cust.friendlyname == row[0] and cust.codename == row[1]:
											m = MailDomain(
												domainname = row[3],
												testuser = row[2],
												failing = False,
												maintmode = False,
												customer = cust
											)
											m.save(force_insert=True)
											c_newly_imported_domains += 1
								else:
									c_domains_with_errors += 1
									print 'WARNING!!!!!!!!!!!!!!!!\ncheck that there are no typos in this email address: ' + strng + '.\n---------------------------------------------\n---------------------------------------------'
							if counter == 1:
								#if counter == 1, there is already such a MailDomain object
								c_already_in_md += 1
					print '%s' % c_newly_imported_domains + ' maildomains have been imported during the most recent addmaildomains.py run'
					print '%s' % c_already_in_md + ' maildomains were already in maildomain database when addmaildomains.py tried to import them from csv file'
					print '%s' % c_domains_with_errors + ' rows are problematic -- likely have typos.'
#this c counts the number of correct items in the csv file that are
#already in maildomain db
					print '%s' % row_count + ' rows total in csv file except for the sample row that starts with "Customer.friendlyname".\n%s is the sum of maildomains that were already in maildomains db, problematic and recently imported.' % (c_newly_imported_domains + c_domains_with_errors + c_already_in_md)		#this counts the number of rows in csv database
					if row_count != (c_newly_imported_domains + c_domains_with_errors + c_already_in_md):
						print 'THE TWO NUMBERS ABOVE MUST BE EQUAL! MAKE SURE THAT EACH ROW HAS 4 ITEMS SEPARATED BY 3 COMMAS'
			else:
				print 'create Config object 1 and fill out all the fields in Config object no.1!!!!!!!!!!!!!!!!!'
		except IOError, e:
			print "Oh no! Bad file! %s" % e
		
		if __name__ == "__handle__":
			handle()
