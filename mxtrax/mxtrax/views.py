from django.http import HttpResponse
import datetime
from datetime import timedelta
from mxtrax.models import MailDomain, Stat
import json
from django.shortcuts import render_to_response
import time
import random

def demo_linewithfocuschart(request, mdomain="0"):
	d_diff = 0
	start_date = datetime.date(2000, 1, 1)
	end_date = datetime.date(2000, 1, 1)

	for md in MailDomain.objects.all():
		md_name = md.testuser + '@' + md.domainname
		if md_name == mdomain:

			start_date = datetime.date(2000, 1, 1)
			end_date = datetime.date(2000, 1, 1)
			for stat in Stat.objects.filter(domain=md):
				if end_date == datetime.date(2000, 1, 1) or stat.d > end_date:
					end_date = stat.d
				if start_date == datetime.date(2000, 1, 1) or stat.d < start_date:
					start_date = stat.d

			d_diff = (end_date - start_date).days + 1
			start_time = int(time.mktime(datetime.datetime(start_date.year, start_date.month, start_date.day).timetuple()) * 1000)
			xdata = range(d_diff)
			xdata = [(start_time + (i * 86400000)) for i in range(d_diff)]

			ydata = [(0 if not Stat.objects.filter(domain=md, d=start_date+timedelta(days=i)).exists() else Stat.objects.get(domain=md, d=(start_date+datetime.timedelta(days=i))).min_delivery_time) for i in range(d_diff)]
			ydata2 = [(0 if not (Stat.objects.filter(domain=md, d=start_date+timedelta(days=i)).exists() and ((Stat.objects.get(domain=md, d=(start_date+datetime.timedelta(days=i))).ontime_num > 0) or (Stat.objects.get(domain=md, d=(start_date+datetime.timedelta(days=i))).late_num > 0))) else (Stat.objects.get(domain=md, d=(start_date+datetime.timedelta(days=i))).total_delivery_time)/(Stat.objects.get(domain=md, d=(start_date+datetime.timedelta(days=i))).ontime_num + Stat.objects.get(domain=md, d=(start_date+datetime.timedelta(days=i))).late_num)) for i in range(d_diff)]
			ydata3 = [(0 if not Stat.objects.filter(domain=md, d=start_date+timedelta(days=i)).exists() else Stat.objects.get(domain=md, d=(start_date+datetime.timedelta(days=i))).max_delivery_time) for i in range(d_diff)]

#		k = 2
#		if (num == ('%s' % k)):
#			ydata4 = [0 for i in range(d_diff)]
#		else:
#			ydata4 = [0 for i in range(d_diff)]


			tooltip_date = "%d %b %Y. maildomain: " + md_name
			extra_serie = {"tooltip": {"y_start": "Time: ", "y_end": " seconds"}, "date_format": tooltip_date}
			chartdata = {
				'x': xdata,
				'name1': 'min delivery time', 'y1': ydata, 'extra1': extra_serie,
				'name2': 'avg delivery time', 'y2': ydata2, 'extra2': extra_serie,
				'name3': 'max delivery time', 'y3': ydata3, 'extra3': extra_serie,
			}
			charttype = "lineWithFocusChart"
			data = {
				'charttype': charttype,
				'chartdata': chartdata
			}
			return render_to_response('linewithfocuschart.html', data)
