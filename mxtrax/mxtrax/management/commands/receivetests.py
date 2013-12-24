#Author: Misha Ignatenko <mykhaylo.ignatenko@citon.com>
#Copyright: Citon Computer Corp
#last edit: July 22, 2013
#description: the programs scans the mbox file for incoming emails.
#if a MailTest object's subject line matches any part of a subject line of an
#mbox message, then the program updates MailTest.receivetime. We need a reg
#expression for uuid4 model because subjects of emails that were bounced back
#may be changed. i.e.: 'RE: ' may be added, etc. if a matching email is found,
#MailTest receivetime is updated and that message is removed from mbox file
#so that it doesn't get clustered.

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from mxtrax.models import Customer, MailDomain, MailTest, Config, Stat
from django.core.mail import send_mail
import mailbox
import datetime
from datetime import date
from datetime import time
import uuid
import re
from pytz import timezone
import dateutil.parser as dparser
import os, sys, stat
from django.core.validators import email_re

class Command(BaseCommand):
	description = """please refer to readme.txt for detailed description of the program."""

	option_list = BaseCommand.option_list + (make_option('--long', '-1', dest='long', help='Help for the long options'),)

	help = 'The purpose of this program is to look at the mbox file that receives emails that were bounced back, match each message that was properly bounced back to a MailTest object and update the receivetime field in MailTest, which corresponds to when the email bounced back.\nThe program will only send a report to the email address specified in Config if at least one maildomain in the database is marked as failing, regardless of maintenance mode status of any maildomain in the database. Here are some items that you need to verify before running the program:\n1)Make sure there is one object in Config based on which the program will run\n2)Make sure that all fields in object 1 of Config are filled out.'
	def handle(self, **options):

		#first check if object 1 in Config doesn't have any empty fields
		if Config.objects.filter(id=1).exists():
#			print date.today()
#		if Config.objects.get(id=1).sendinguser!=None and Config.objects.get(id=1).maxreturntime!=None and Config.objects.get(id=1).alertuser!=None and Config.objects.get(id=1).mboxpath!=None and Config.objects.get(id=1).maxfailnumber!=None and Config.objects.get(id=1).maxfailpercentage!=None and Config.objects.get(id=1).maxlatenumber!=None and Config.objects.get(id=1).maxlatepercentage!=None:
			#this constructs a sendinguserstr. mbox file format
			#will have email senders as <sender@example.com>
			sendinguserstr = '<' + Config.objects.get(id=1).sendinguser +'>'
			#this is a regular expression that sets the model for
			#UUID. The program will look for UUIDs in the subject
			#of every incoming email.
			#due to the different auto-reply settings, some other
			#string may be appended to the UUID in the subject line
			#this is why we need a model to look for and extract
			#UUID to match with each MailTest object and update
			#receivetime
			emailpattern = re.compile("[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}")
			try:
				with open(Config.objects.get(id=1).mboxpath):
#Jul 18 indented everything below by 2 tabs
					destination = mailbox.mbox(Config.objects.get(id=1).mboxpath)
					st = os.stat(Config.objects.get(id=1).mboxpath)
			#this try clause will try to get a message from mbox
			#file, match its subject to a MailTest object and
			#update MailTest.receivetime for that object as well
			#as delete the message from mbox after processing it
			#so that mbox file is not clustered with processed
			#emails
					if not bool(st.st_mode & stat.S_IRUSR) == True and bool(st.st_mode & stat.S_IWUSR):
						print 'ERRORRRRRRRRRRRR'
						print 'does owner have user permissions to read the mbox file? - %s' % bool(st.st_mode & stat.S_IRUSR)
						print 'does owner have user permissions to edit the mbox file? - %s' % bool(st.st_mode & stat.S_IWUSR)
						sys.exit(1)
					else:
						try:
							statinfo = os.stat(Config.objects.get(id=1).mboxpath)
							#we need to lock the mbox file so that no emails arrive while the scan is in session
							destination.lock()
							for messagekey in destination.keys():

								try:
									message = destination[messagekey]
									subject_match = emailpattern.search(message['Subject'])
									if hasattr(subject_match, "group") == True:
										full_uuid_str = subject_match.group(0)
										for mt in MailTest.objects.all():
									#a successfully bounced back email would have a UUID somewhere in its subject line
#!!!!!!!!!!!!!!!
#THE PROGRAM ONLY SCANS MBOX FILE AND ATTEMPTS TO PARSE RECEIVE TIME IF MAXRETURN TIME HAS PASSED SINCE SENDTIME FOR THAT MAILTEST
#if full_uuid_str == mt.receiveheaders and message['From'] == sendinguserstr and datetime.datetime.now() > mt.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime):
											if full_uuid_str == mt.testid and message['From'] == sendinguserstr and datetime.datetime.now() > mt.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime):
												message_get_from_full_string = '%s' % message.get_from()
												get_from_line_without_mt_maildomain = message_get_from_full_string.replace('%s ' % mt.maildomain, '')
												mt.receivetime = dparser.parse('%s' % get_from_line_without_mt_maildomain)
												mt.save()
												destination.__delitem__(messagekey)	#this deletes the message that was successfully processed
								except ValueError:
									print 'there is a problem with message with subject: %s' % message['Subject']
						except ValueError:
							print 'there is a problem with message with at least one email in mxtrax mbox file.'
						except PermissionError:
							print 'Switch to the user that has access rights for %s' % Config.objects.get(id=1).mboxpath
						finally:
							destination.close()	#this saves the changes to the mbox file and closes it
							#we need to chown back into the statinfo of the mbox file. otherwise, we can get kicked out into "root" ownership
							os.chown(Config.objects.get(id=1).mboxpath, statinfo.st_uid, statinfo.st_gid)
							destination.unlock()	#unlock mbox to allow incoming mail

			except IOError, e:
				print 'please provide the correct, absolute path to mbox file! %s' % e

			#these variables will be used to calculate OVERALL
			#on-time, late and not bounced back statistics
			overall_ontime_num = 0	#on time for all domains, overall
			overall_late_num = 0	#late for all domains, overall
			overall_nobounce_num = 0	#did not bounce back for all domains, overall
			for obj in MailTest.objects.all():
				if obj.receivetime != None and obj.receivetime <= obj.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime) and datetime.datetime.now() > obj.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime):
					overall_ontime_num += 1
			#this finds the number of tests that weren't returned
			for objct in MailTest.objects.all():
				if objct.receivetime == None and datetime.datetime.now() > objct.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime):
					overall_nobounce_num += 1
			#this finds the number of late tests in all MailTest
			#objects
			for objt in MailTest.objects.all():
				if objt.receivetime != None and objt.receivetime > objt.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime) and datetime.datetime.now() > objt.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime):
					overall_late_num += 1




#NOW WE CALCULATE STATS FOR EACH MAILDOMAIN
			#max number of not bounced back
			max_failing_number = Config.objects.get(id=1).maxfailnumber
			#max not bounced back percentage
			max_failing_percentage = Config.objects.get(id=1).maxfailpercentage*1.00
			#maximum allowed number of late emails
			max_late_number = Config.objects.get(id=1).maxlatenumber
			#max allowed percentage of late emails
			max_late_percentage = Config.objects.get(id=1).maxlatepercentage*1.00

			stats_str = '\nMAX late number limit: %s' % max_late_number + '\nMAX late percentage limit: %.2f' % max_late_percentage + '\nMAX not bounced back number limit: %s' % max_failing_number + '\nMAX not bounced back percentage limit: %.2f' % max_failing_percentage
			stats_str += '\nHere are some stats for each domain:'
			for stats_obj_domain in MailDomain.objects.all():
				if stats_obj_domain.maintmode == False:		#this is so that you only get a report for those maildomains not in maintmode
					stats_str += '\n\nstats for: %s' % stats_obj_domain
					avg_t_total = datetime.timedelta(0)
					for avg_delivery_t_object in MailTest.objects.all():
						if avg_delivery_t_object.receivetime != None and stats_obj_domain == avg_delivery_t_object.maildomain:
							avg_t_total += avg_delivery_t_object.receivetime - avg_delivery_t_object.sendtime
					domain_ontime_num = 0	#number of successful tests for a specific domain
					domain_late_num = 0	#number of late tests for a specific domain
					domain_nobounce_num = 0	#number of tests that didn't bounce back from a specific domain
					for stats_obj_mailtest in MailTest.objects.all():
						if stats_obj_domain == stats_obj_mailtest.maildomain and stats_obj_mailtest.receivetime != None and stats_obj_mailtest.receivetime <= stats_obj_mailtest.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime) and datetime.datetime.now() > stats_obj_mailtest.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime):
							domain_ontime_num += 1
						elif stats_obj_domain == stats_obj_mailtest.maildomain and stats_obj_mailtest.receivetime != None and stats_obj_mailtest.receivetime > stats_obj_mailtest.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime) and datetime.datetime.now() > stats_obj_mailtest.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime):
							domain_late_num += 1
						elif stats_obj_domain == stats_obj_mailtest.maildomain and stats_obj_mailtest.receivetime == None and datetime.datetime.now() > stats_obj_mailtest.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime):
							domain_nobounce_num += 1
					stats_str += '\non time: %s' % domain_ontime_num
					stats_str += '\nlate: %s' % domain_late_num
					stats_str += '\ndid not bounce back: %s' % domain_nobounce_num


					if domain_ontime_num>0 or domain_late_num>0:
						stats_str += '\naverage delivery time: %s.' % (avg_t_total/(domain_ontime_num+domain_late_num))
					else:
						stats_str += '\nthere are no successful or late tests - cannot calculate average delivery time.'

					if domain_ontime_num>0 or domain_late_num>0 or domain_nobounce_num>0:
						stats_str += '\non-time rate is: %.2f percent' % (100.00*(domain_ontime_num)/(domain_ontime_num+domain_late_num+domain_nobounce_num))
						stats_str += '\nlate rate: %.2f percent' % (100.00*(domain_late_num)/(domain_ontime_num+domain_late_num+domain_nobounce_num))
						stats_str += '\nnot bounced back rate: %.2f percent' % (100.00*(domain_nobounce_num)/(domain_ontime_num+domain_late_num+domain_nobounce_num))
						if domain_nobounce_num <= max_failing_number and (100.00*(domain_nobounce_num)/(domain_ontime_num+domain_late_num+domain_nobounce_num)) <= max_failing_percentage and domain_late_num <= max_late_number and (100.00*(domain_late_num)/(domain_ontime_num+domain_late_num+domain_nobounce_num)) <= max_late_percentage:
							#mark such domain as NOT failing if it meets all these restrictive conditions
							stats_obj_domain.failing = False
							stats_obj_domain.save()
						else:
							if domain_nobounce_num > max_failing_number:
								stats_str += '\ndomain exceeded the max not bounced back number limit'
							if (100.00*(domain_nobounce_num)/(domain_ontime_num+domain_late_num+domain_nobounce_num)) > max_failing_percentage:
								stats_str += '\ndomain exceeded the max not bounced percentage limit'
							if domain_late_num > max_late_number:
								stats_str += '\ndomain exceeded the max late number limit'
							if (100.00*(domain_late_num)/(domain_ontime_num+domain_late_num+domain_nobounce_num)) > max_late_percentage:
								stats_str += '\ndomain exceeded the max late percentage limit'
							#mark such maildomain as failing if any of the restrictive conditions in the if clause above is not met
							stats_obj_domain.failing = True
							stats_obj_domain.save()
					if domain_ontime_num==0 and domain_late_num==0 and domain_nobounce_num==0:
						stats_str += '\nyou do not have any mailtests for %s.' % stats_obj_domain
#for ratio make sure you're not dividing by zero
					n_of_mailtests_for_each_maildomain = 0
					for objctt in MailTest.objects.all():
						if stats_obj_domain == objctt.maildomain:
							n_of_mailtests_for_each_maildomain += 1
					if n_of_mailtests_for_each_maildomain != (domain_ontime_num+domain_late_num+domain_nobounce_num):
						stats_str += '\nERROR!!!!! not all mailtests were included in stats for %s' % stats_obj_domain
					if stats_obj_domain.failing == True:
						stats_str += '\nIs this domain marked as failing? - YES'
					else: stats_str += '\nIs this domain marked as failing? - NO'
					stats_str += '\n----------------------------------------------------------------------------------------------------------------'
				else:
					stats_str += '\nno stats for this domain because it is in maintenance mode: %s.' % stats_obj_domain
			#this calculates overall average delivery time for all
			#maildomains combined
			avg_t_total = datetime.timedelta(0)
			for avg_delivery_t_object in MailTest.objects.all():
				if avg_delivery_t_object.receivetime != None:
					avg_t_total += avg_delivery_t_object.receivetime - avg_delivery_t_object.sendtime
#send alert-------------------------------------------------------------------
			str = ''
			for m in MailDomain.objects.all():
				if m.maintmode != True and m.failing == True:
					str += 'this domain is failing: %s' % m + '\n'

			if overall_ontime_num>0 or overall_late_num>0 or overall_nobounce_num>0:
				str += 'overall on-time rate is: %.2f percent.' % (100.00*overall_ontime_num/(overall_ontime_num+overall_late_num+overall_nobounce_num))
			else:
				str += 'no items in MailTest database.'
			str += '\non time: %s.' % overall_ontime_num
			str += '\nlate: %s.' % overall_late_num
			str += '\ndid not return: %s.' % overall_nobounce_num
			str += '\ntotal: %s.' % (overall_ontime_num+overall_late_num+overall_nobounce_num)
			#get the total time from those mailtests that have both
			#sendtime and receivetime, and divide by the number
			#of on-time plus late emails
			if overall_ontime_num>0 or overall_late_num>0:
				str += '\naverage delivery time: %s.' % (avg_t_total/(overall_ontime_num+overall_late_num))
			else:
				str += '\nthere are no successful or late tests - cannot calculate average delivery time.'
			#this is to make sure that all MailTest objects have
			#been counted in the overall stats
			total_number_of_MailTests = 0
			for i in MailTest.objects.all():
				if datetime.datetime.now() > i.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime):
					total_number_of_MailTests += 1
			if total_number_of_MailTests != (overall_ontime_num+overall_late_num+overall_nobounce_num):
				str += '\nERRORRRRRR!! some objects that are in MailTest db are not included in the report!'
			str += stats_str	#adding stats string for each domain to the alert email string!!!!!!!!!!!!!!!!!!
			boo = False
			#if at least one MailDomain is failing, then you will
			#get an email report, even if all of them are in
			#maintmode if no MailDomains are failing, you will not
			#get an email report
			for fail_dom in MailDomain.objects.all():
				if fail_dom.failing == True and fail_dom.maintmode == False:
					boo = True
			if boo == True:
				if email_re.match(Config.objects.get(id=1).alertuser):
					send_mail('MXTRAX alert', '%s' % str, 'DO-NOT-REPLY', [Config.objects.get(id=1).alertuser], fail_silently=False)
				else:
					print 'WARNING!!!!!!!!!!!!!!!!!!!!\ncheck spelling of alertuser in Config!!!!!!!!'



			if not Config.objects.get(id=1).maxreturntime <= Config.objects.get(id=1).max_sec_until_fail:
				print 'in Config, make sure that the hard limit on return time is bigger than maxreturntime!!!!!!!!!!!\nstats might not have been calculated correctly because of this.'


			for mdomain in MailDomain.objects.all():
				#NOW need to create all possible STat objects with combinations of sendtime dates for each maildomain
				for mail_test in MailTest.objects.filter(maildomain=mdomain):
					#if a Stat objects with a given date and domain doesn't exist, we need to create it
					if not Stat.objects.filter(domain=mdomain, d=datetime.date(mail_test.sendtime.year, mail_test.sendtime.month, mail_test.sendtime.day)).exists():
						m = Stat(
							d=datetime.date(mail_test.sendtime.year, mail_test.sendtime.month, mail_test.sendtime.day),
							domain=mdomain,
							total_delivery_time=0,
							total_num=0,
							ontime_num=0,
							late_num=0,
							fail_num=0
						)
						m.save(force_insert=True)

				#now that all Stat objects have been created, we can scan MailTest and update the corresponding Stat objects

				#this only looks at MailTests that haven't yet been processed, i.e. not yet included in stats
				for mailtest_for_stat in MailTest.objects.filter(maildomain=mdomain, incl_in_stat=False):
					#k is the corresponding Stat object for that MailTest
					#we want to update k accordingly and mark mailtest_for_stat as processed
					for k in Stat.objects.filter(domain=mdomain, all_done=False, d=datetime.date(mailtest_for_stat.sendtime.year, mailtest_for_stat.sendtime.month, mailtest_for_stat.sendtime.day)):
						#first, we process MailTests that have a receivetime
						if mailtest_for_stat.receivetime != None:
							if k.max_delivery_time == None:
								k.max_delivery_time = -1
		#we don't want to count as max delivery time the receivetime for a MailTest that passed hard delivery time limit
							if k.max_delivery_time == -1 or (k.max_delivery_time >= 0 and k.max_delivery_time <= (mailtest_for_stat.receivetime - mailtest_for_stat.sendtime).days * 86400 + (mailtest_for_stat.receivetime - mailtest_for_stat.sendtime).seconds and mailtest_for_stat.receivetime <= mailtest_for_stat.sendtime + datetime.timedelta(0, Config.objects.get(id=1).max_sec_until_fail)):
								k.max_delivery_time = (mailtest_for_stat.receivetime - mailtest_for_stat.sendtime).days * 86400 + (mailtest_for_stat.receivetime - mailtest_for_stat.sendtime).seconds

							if k.min_delivery_time == None:
								k.min_delivery_time = -1
		#we don't want to count as max delivery time the receivetime for a MailTest that passed hard delivery time limit
							if k.min_delivery_time == -1 or (k.min_delivery_time >= 0 and k.min_delivery_time >= (mailtest_for_stat.receivetime - mailtest_for_stat.sendtime).days * 86400 + (mailtest_for_stat.receivetime - mailtest_for_stat.sendtime).seconds and mailtest_for_stat.receivetime <= mailtest_for_stat.sendtime + datetime.timedelta(0, Config.objects.get(id=1).max_sec_until_fail)):
								k.min_delivery_time = (mailtest_for_stat.receivetime - mailtest_for_stat.sendtime).days * 86400 + (mailtest_for_stat.receivetime - mailtest_for_stat.sendtime).seconds

							if mailtest_for_stat.receivetime <= mailtest_for_stat.sendtime + datetime.timedelta(0, Config.objects.get(id=1).max_sec_until_fail):
								k.total_delivery_time += ((mailtest_for_stat.receivetime - mailtest_for_stat.sendtime).days * 86400 + (mailtest_for_stat.receivetime - mailtest_for_stat.sendtime).seconds)
							if mailtest_for_stat.receivetime <= mailtest_for_stat.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime):
								k.ontime_num += 1
							if mailtest_for_stat.receivetime > mailtest_for_stat.sendtime + datetime.timedelta(0, Config.objects.get(id=1).maxreturntime) and mailtest_for_stat.receivetime <= mailtest_for_stat.sendtime + datetime.timedelta(0, Config.objects.get(id=1).max_sec_until_fail):
								k.late_num += 1
							#if an email bounced back but took longer than hard limit, we still
							#want to count it as failing
							if mailtest_for_stat.receivetime > mailtest_for_stat.sendtime + datetime.timedelta(0, Config.objects.get(id=1).max_sec_until_fail):
								k.fail_num += 1

							mailtest_for_stat.incl_in_stat = True
							mailtest_for_stat.save()
							k.save()
						#if an email still hasn't bounced back when hard limit has passed since
						#its sendtime, we should mark it as failing
						if mailtest_for_stat.receivetime == None and datetime.datetime.now() > mailtest_for_stat.sendtime + datetime.timedelta(0, Config.objects.get(id=1).max_sec_until_fail):
							k.fail_num += 1
							mailtest_for_stat.incl_in_stat = True
							mailtest_for_stat.save()
							k.save()

				#calculate how many MailTest objects have no receivetime and update total_num in Stat
				for st in Stat.objects.filter(domain=mdomain, all_done=False):
					mt_not_processed_no_receive_time_num = 0
					for mtst in MailTest.objects.filter(maildomain=mdomain, receivetime=None, incl_in_stat=False):
						if datetime.date(mtst.sendtime.year, mtst.sendtime.month, mtst.sendtime.day) == st.d:
							mt_not_processed_no_receive_time_num += 1
					st.total_num = mt_not_processed_no_receive_time_num + st.ontime_num + st.late_num + st.fail_num
					st.save()
					#mark Stat the following day if total_num==ontime_num+late_num+fail_num
					if datetime.datetime.now().date() > st.d and st.total_num == st.ontime_num + st.late_num + st.fail_num:
						st.all_done = True
						st.save()
					

		else:
			print 'create Config object 1 and fill out all the fields on Config object no.1!!!!!!!!!!!!!!!!!'
