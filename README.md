mxtrax
======

Mail Exchange Round Trip Time
by Misha Ignatenko <mykhaylo.ignatenko@citon.com>

Description of the program.
The purpose of this program is to check if your customers' email domains are working properly. Before running the program you need to create a test email box at each domain that you host AND set this email box to return/bounce back all incoming emails. All returned emails will be recorded in the mbox file associated with Config.sendinguser email address. When an email returns from a test mail box that is set up auto-reply, the sender email will be the email from which the email was initially sent (if full_uuid_str == mt.receiveheaders and message['From'] == sendinguserstr: )! Once you have set up all the test email boxes at each of your customers' email domains, make a CSV file in the following format:
Customer.friendlyname,Customer.codename,MailDomain.testuser,MailDomain.domainname
customer,full_customer_name,email,example.com  		<-- i.e. the email address of this customer is email@example.com
…

Before you schedule sendtests and receivetests crontab jobs, you need to make sure that you have created and synced mxtrax.db
cd mxtrax
python manage.py sql mxtrax
python manage.py syncdb

Run the program in you browser and add a Config object. The program will run based on the info that you enter:
sendinguser - email address from which you will be sending email tests and to which emails will be bounced back
maxreturntime - max allowed roundtrip time for all email tests
alertuser - email address to which the program will send a report if at least one MailDomain is failing
mboxpath - absolute path to mbox file that will receive emails that bounce back. This mbox is associated with sendinguser email address
maxfailnumber - max allowed number of email that a given MailDomain did not return. If a MailDomain exceeds this number, it will be marked as failing.
maxfailpercentage - max allowed percentage of emails for every MailDomain that did not return divided by the total number of emails (MailTest entries) that were send to that MailDomain. If a MailDomain exceeds this percentage, it will be marked as failing.
maxlatenumber - max allowed number of emails that took longer to return than maxreturntime mentioned above. If a MailDomain exceeds this number, it will be marked as failing.
maxlatepercentage - max allowed percentage of emails that took longer to return than maxreturntime divided by the total number of MailTests for that MailDomain. If a MailDomain exceeds this percentage, it will be marked as failing.

mxtrax->mxtrax->management->commands->addmaildomains.py
The purpose of addmaildomains.py is to import info from your customer CSV file into Customer and MailDomain databases. You will get an error message (i.e. file does not exist, you forgot to include -f etc.) if you do not run "python manage.py addmaildomains -f [absolute path to your CSV file]". Addmaildomains will also print out statistics of how many MailDomains were imported, how many weren't imported because they are already in MailDomains database, and how many weren't imported because they did not pass email validation test (i.e. have typos in them). Addmaildomains will also verify that the total number of lines (excluding the first sample row "Customer.friendlyname,Customer.codename,MailDomain.testuser,MailDomain.domainname") in CSV file equals the sum of MailDomains that were imported, already in MailDomain db and those that have typos.

mxtrax->mxtrax->management->commands->sendtests.py
Sendtests.py sends emails to all objects in MailDomains database that are not marked as "in maintenance mode" and creates corresponding MailTest objects for each sent email with an empty receivetime field (since the email hasn't yet been detected as received) and UUID in receiveheaders field.

mxtrax->mxtrax->management->commands->receivetests.py
Receivetests.py checks if absolute path that you provided in Config.mboxpath is valid and if the current user has permissions to access mbox file. Receivetests.py scans the mbox file, tries to match each MailTest object with messages in mbox file by validating UUIDs in messages' subject lines. Some auto-reply settings may add something like "Re: " to the subject line, so we need to use regular expressions to match subject lines of mbox messages and MailTests' subject lines. If an email is undeliverable, your mbox file will get a mailer daemon message, which will not be mistakenly takes as successfully bounced back -- an email from mailer daemon will not have sendinguser as sender email. It is important to use both validators while matching mbox messages with MailTest objects: UUID in subject line and sender email address. If there is a match, receivetests.py will get the received time from mbox message and update the corresponding MailTest.receivetime. Mbox messages (regardless of if it is late or on-time) are deleted from mbox file so that it doesn't get clustered with successfully processed info and instead contains only the info that needs further investigation. If an email test never bounced back to mbox file, then the corresponding MailTest object will have a blank receivetime field. Receivetests.py verifies that send alerts email address is spelled correctly and send a report only if at least one of MailDomains is marked as failing, regardless of its maintenance mode status. The email report will provide a list of MailDomains that are marked as "failing" and "not in maintenance mode", overall statistics (average on-time percentage, overall on-time, late and not bounced back numbers, average time it took on-time and late emails to bounce back), and statistics for each MailDomain that is not marked as "in maintenance mode" (on-time, late and not bounced back numbers and percentages as well as whether it is marked as "failing").

Still working on writing coding for Stat, which will enable the user to display statistics for the selected timeframe and MailDomain.
