import urllib2
from front_end.models import *
from main.models import Countries
from django.template.defaultfilters import slugify

class LocationMiddleware(object):
	def process_view(self, request, index, view_args, view_kwargs):
		if not request.session.get('city'):
			ip = request.META['REMOTE_ADDR']
			if ip == '127.0.0.1':
				ip = '72.99.237.123'
			if ip:
				f = urllib2.urlopen('http://api.ipinfodb.com/v3/ip-city/?key=a13198e66f807a846e1f2b7ad4f5e0027735d56109dc3b114f5a330da411bfc5&ip='+ip)
				str = f.read()
				status = str.split(';;')[0]
				code = str.split(';;')[-1]
				if status == 'OK':
					ip, country_code, country, state, city, postal_code, latitude, longitude, time_zone = code.split(';')
					request.session['city'] = city
					request.session['latitude'] = latitude
					request.session['longitude'] = longitude
					request.session['country'] = country
					                   
					#Save this info to the db
					#if not request.user.is_anonymous():
					#profile = request.user.get_profile()
					try:
						current_country = Countries.objects.get(code=country_code)
					except:
						current_country ,created =Countries.objects.get_or_create(name=country,code=country_code)
					current_city ,created = City.objects.get_or_create(name=city,country=current_country,slug=slugify(city),live=True)
					current_state ,created = State.objects.get_or_create(name=state)
					current_address, created = Address.objects.get_or_create(latitude=latitude, longitude=longitude, city=current_city,state=current_state,name = country)
		return None
