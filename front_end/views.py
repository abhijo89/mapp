from django.contrib.auth.models import check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson
from main.form import *
from main.models import *
from django.contrib.auth import authenticate, login, logout
from helper import *
from models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMessage
from django.core.paginator import Paginator

paginator_total_result_count = 50

def extra_context(paginator, all_results):
	return  {'base_url' : None,
			'is_paginated' : all_results.has_other_pages(),
			'pages': paginator.num_pages,
			'page': all_results.number,
			'results_per_page': paginator.per_page,
			'has_next': all_results.has_next(),
			'has_previous': all_results.has_previous(),
			'next': all_results.next_page_number(),
			'previous': all_results.previous_page_number(),
			'first_on_page': all_results.start_index(),
			'last_on_page': all_results.end_index(),
			'pages': paginator.num_pages,
			'hits': paginator.count,
			'page_range': paginator.page_range, }
			
#Functions 
def sendusermail(email):
	body = '''
			Hi, 

			Thank you for subscribing with MuviDB. Your login link is http://www.muvidb.com

			Thanks,
			MuviDB team
			'''
	email = EmailMessage('Thank you for subscribing to MuviDB', body, 'noreply@muvidb.com',[email])
	adminmail=EmailMessage('New User loged in',email,['admin@muvidb.com',])
	adminmail.send(fail_silently=True)
	email.send(fail_silently=True)
	return True
	
def contactview(request):
		subject = request.POST.get('topic', '')
		message = request.POST.get('message', '')
		from_email = request.POST.get('email', '')

		if subject and message and from_email:
			try:
					email =  EmailMessage(subject, message, from_email, ['admin@muvidb.com'])
					email.send(fail_silently=True)
			except :
				return HttpResponse('Invalid header found.')
				return HttpResponseRedirect(reverse('index'))
		else:
			return render_to_response('main/contacts.html', {'form': ContactForm()},context_instance = RequestContext(request))
	
		return render_to_response('main/contacts.html', {'form': ContactForm()},
			context_instance = RequestContext(request))
def thankyou(request):
		return render_to_response('thankyou.html')
def register_view(request,template='popup/register.html'):
	form = RegistrationForm()
	context={'form':form }
	return render_to_response(template, context, context_instance = RequestContext(request)) 
	
@csrf_exempt
def register(request,to_return=''):
	if request.method == 'POST':
			form = RegistrationForm(data=request.POST, files=request.FILES)
			if form.is_valid():            
					new_user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password1'])
					new_user.save()
					user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
					profile = UserProfile.objects.create(user=new_user) 
					profile.send_me_daily_email=False
					profile.save()
					sendusermail(form.cleaned_data['email'])
					login(request, user)
					to_return={'success':True ,'url':reverse('edit_profile_page')}
					#return HttpResponseRedirect(reverse('edit_profile_page'))
			else:
				to_return={'success':False,'message':''}
	return HttpResponse(simplejson.dumps(to_return), mimetype='application/json')
	
def myaccount(request,user_id=None):
	user = request.user
	if user.is_anonymous():
			return HttpResponseRedirect(reverse('index'))
	profile=user.get_profile()
	city = False
	if user_id == None:
		if user.is_anonymous():
			return HttpResponseRedirect(reverse('index'))
	else:
		user = User.objects.get(id=int(user_id))
		#city = user.get_profile().city
	context={'profile':profile ,'page_user':user}
	return render_to_response('main/myaccount.html', context, context_instance = RequestContext(request))
	
def friend_request(request, user_id):
	user = request.user
	requested_user = User.objects.get(id=user_id)
	friend, created = Friend.objects.get_or_create(user_requesting=user, user_accepting=requested_user)
	to_return = { 'message' : 'success', 'success' : True }
	return HttpResponse(simplejson.dumps(to_return), mimetype='application/json')
	
def friend_accept(request, user_id):
	user = request.user
	requesting_user = User.objects.get(username=user_id)
	friend = Friend.objects.get(user_requesting=requesting_user, user_accepting=user)
	friend.are_friends = True
	friend.save()
	profile = user.get_profile()
	profile.friends.add(requesting_user)
	profile.save()
	to_return = { 'message' : 'success', 'success' : True }
	return HttpResponse(simplejson.dumps(to_return), mimetype='application/json')

def edit_profile_page(request):
	current_password = request.POST.get('current_password', '')
	new_password = request.POST.get('new_password', '')
	confirm_password = request.POST.get('confirm_password', '')
	password_error = ''
	country=Countries.objects.all()
	if request.POST:
		gender = request.POST.get('gender', '')
		first_name = request.POST.get('first_name', '')
		last_name = request.POST.get('last_name', '')
		email = request.POST.get('email', '')
		day = request.POST.get('day', '')
		month = request.POST.get('month', '')
		year = request.POST.get('year', '')
		city= request.POST.get('city')
		country= request.POST.get('country')
		user = request.user
		user.first_name = first_name
		user.last_name = last_name
		user.email = email
		user.get_profile().gender = gender
		country_obj=Countries.objects.get(name=country)
		if City.objects.filter(name=city):
			city_name=City.objects.get(name=city)
		else :
			city_name,c = City.objects.get_or_create(name=city,country=country_obj,slug=country+'_'+city)
		user.get_profile().city=city_name
		
		
		if day.isdigit() and month.isdigit() and year.isdigit():
			date = datetime.date(int(year), int(month), int(day))
			user.get_profile().birthday = date

		if current_password:
			if not new_password or not confirm_password:
				password_error = 'All fields are required'
			if not password_error:
				if check_password(current_password, user.password ):
					if new_password == confirm_password:
						user.set_password(new_password)
						user.get_profile().has_blank_password = False
						password_error = 'Your password has been updated successfully.'
					else:
						password_error = 'The two passwords don\'t match'
				else:
					password_error = 'The current password you entered doesn\'t match our records.'

		user.save()
		user.get_profile().save()

	context = { 'days' : range(1, 32), 'months' : MONTHS, 'years' : range(1900, 2012), 'current_password' : current_password, 'new_password' : new_password,
			   'confirm_password' : confirm_password, 'password_error' : password_error,'country':country }
	
	return render_to_response('main/edit_profile_page.html', context, context_instance = RequestContext(request))


def profile_pic(request):
	profile = request.user.get_profile()
	profile_pic_changed = False
	default_pic = False

	if request.method == 'POST':
		if request.FILES['profile_pic']:
			profile.profile_pic = request.FILES['profile_pic']
			profile.save()
			profile_pic_changed = True

	if profile.profile_pic == 'images/profile_pics/profile.png':
		default_pic = True

	context = {'profile_pic_changed': profile_pic_changed, 'default_pic' : default_pic }
	return render_to_response('main/profile_pic.html', context, context_instance = RequestContext(request))
	
def delete_pic(request):
	profile = request.user.get_profile()
	profile.profile_pic = 'images/profile_pics/profile.png'
	profile.save()
	import json
	to_return = {'message' : 'Profile picture reset ...', 'success' : True }
	return HttpResponse(json.dumps(to_return), mimetype='application/json')

#SEARCH 
def search_index(request):
	context = {}
	category ={}
	category ['Country'] = 0
	category ['Language'] = 0
	category ['Genres'] = 0
	context['categorys'] = category
	return render_to_response('main/search_index.html', context, context_instance = RequestContext(request))
	
def search(request,category):
	context ={}
	category = category.title()

	if category == 'Language':
		
		category_item = Languages.objects.all()
	elif category == 'Country':
		category_item = Countries.objects.all()
	elif category == 'Genres':
		category_item = Genre.objects.all()
	context['categorys'] = category_item
	context['category_name'] = category
	return render_to_response('main/search_category.html', context, context_instance = RequestContext(request))
	
def search_movie_by_category(request,category,category_item):
	
	context = {}
	if category == 'Language':	
		category_item = Languages.objects.get(name=category_item)
		movie_list = category_item.Languages_M2M_Movie.all()
	elif category == 'Country':
		category_item = Countries.objects.get(name=category_item)
		movie_list = category_item.Country_M2M_Movie.all()
	elif category == 'Genres':
		category_item = Genre.objects.get(name=category_item)
		movie_list = category_item.Genres_M2M_Movie.all()
	paginator = Paginator(movie_list, paginator_total_result_count) 
	page = int(request.GET.get('page', 1))

	try:
		results_pages = paginator.page(page)
	except : # Standard Exception 
		# If page is out of range (e.g. 9999) or No page found, deliver last page of results.
		results_pages = paginator.page(paginator.num_pages)	
		
	context['categorys'] = results_pages.object_list
	context['category_name'] = category
	context =  dict(context, **extra_context(paginator, results_pages))
	return render_to_response('main/search_movie_list.html', context, context_instance = RequestContext(request))
	
