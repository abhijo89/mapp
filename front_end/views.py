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
	
		return render_to_response('main/thankyou.html', context_instance = RequestContext(request))
def thankyou(request):
		return render_to_response('main/thankyou.html')
		
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
	#if user.is_anonymous():
			#return HttpResponseRedirect(reverse('index'))
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
	user = request.user
	if user.is_anonymous():
			return HttpResponseRedirect(reverse('index'))
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
	user = request.user
	#if user.is_anonymous():
			#return HttpResponseRedirect(reverse('index'))
	context = {}
	category ={}
	category ['Country'] = 0
	category ['Language'] = 0
	category ['Genres'] = 0
	context['categorys'] = category
	return render_to_response('main/search_index.html', context, context_instance = RequestContext(request))
	
def search(request,category):
	user = request.user
	#if user.is_anonymous():
			#return HttpResponseRedirect(reverse('index'))
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
	user = request.user
	#if user.is_anonymous():
			#return HttpResponseRedirect(reverse('index'))
	
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
def search_globel(request):
	context = {}
	query=request.POST.get('q', '')
	if query:
		movie = Movie.objects.filter(title__contains=query)[:1000]
		if not movie :
			movie = get_movie(query)
		paginator = Paginator(movie, paginator_total_result_count) 
		page = int(request.GET.get('page', 1))

		try:
			results_pages = paginator.page(page)
		except : # Standard Exception 
			# If page is out of range (e.g. 9999) or No page found, deliver last page of results.
			results_pages = paginator.page(paginator.num_pages)	
	else :
		return HttpResponseRedirect(reverse('index'))
	context['limit'] = 1
	context['categorys'] = results_pages.object_list
	context['category_name'] = 'Globel'
	context =  dict(context, **extra_context(paginator, results_pages))
	return render_to_response('main/search_movie_list.html', context, context_instance = RequestContext(request))
	
def get_movie(title):
	from imdb import IMDb
	ia = IMDb()
	movie_obj_list = ia.search_movie(title)
	
	for move_obj in movie_obj_list :
		
		save_movie_to_db(move_obj,0,move_obj.data['title'])
	movie = Movie.objects.filter(title__contains=title)[:1000]
	return movie
	
def save_movie_to_db (the_matrix,sucess_factor,movie_name):
	
	tblmovie = fnMovie(the_matrix,sucess_factor,movie_name)
	if not tblmovie:
		return 
	try :
		animation_department = the_matrix.data['animation department']
		for person in animation_department :

			tblperson = fnPerson(person, sucess_factor)
			tblanimation_department, c = Animation_department.objects.get_or_create(name = tblperson)
			tblmovie.animation_department.add(tblanimation_department)
	except Exception as e:
		
		sucess_factor = sucess_factor + 1
		pass
	try :
		art_department = the_matrix.data['art department']
		for person in art_department :

			tblperson = fnPerson(person, sucess_factor)

			tblart_department, c = Art_department.objects.get_or_create(name = tblperson)
			tblmovie.art_department.add(tblart_department)
	except Exception as e:
		sucess_factor = sucess_factor + 1
		pass
	try :
		art_direction = the_matrix.data['art direction']
		for person in art_direction :

			tblperson = fnPerson(person, sucess_factor)

			tblart_direction, c = Art_direction.objects.get_or_create(name = tblperson)
			tblmovie.art_direction.add(tblart_direction)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try :
		assistant_director = the_matrix.data['assistant director']
		for person in assistant_director :

			tblperson = fnPerson(person, sucess_factor)

			tblassistant_director, c = Assistant_director.objects.get_or_create(name = tblperson)
			tblmovie.assistant_director.add(tblassistant_director)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		camera_and_electrical_department = the_matrix.data['camera and electrical department']
		for person in camera_and_electrical_department :

			tblperson = fnPerson(person, sucess_factor)

			tblcamera_and_electrical_department, c = Camera_and_electrical_department.objects.get_or_create(name = tblperson)
			tblmovie.camera_and_electrical_department.add(tblcamera_and_electrical_department)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		casting_department = the_matrix.data['casting department']
		for person in casting_department :

			tblperson = fnPerson(person, sucess_factor)

			tblcasting_department, c = Casting_department.objects.get_or_create(name = tblperson)
			tblmovie.casting_department.add(tblcasting_department)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:

		casting_director = the_matrix.data['casting director']
		for person in casting_director :

			tblperson = fnPerson(person, sucess_factor)

			tblcasting_director, c = Casting_director.objects.get_or_create(name = tblperson)
			tblmovie.casting_director.add(tblcasting_director)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:

		cinematographer = the_matrix.data['cinematographer']
		for person in cinematographer :

			tblperson = fnPerson(person, sucess_factor)

			tblcinematographer, c = Cinematographer.objects.get_or_create(name = tblperson)
			tblmovie.cinematographer.add(tblcinematographer)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		costume_department = the_matrix.data['costume department']
		for person in costume_department :

			tblperson = fnPerson(person, sucess_factor)

			tblcostume_department, c = Costume_department.objects.get_or_create(name = tblperson)
			tblmovie.costume_department.add(tblcostume_department)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		costume_designer = the_matrix.data['costume designer']
		for person in costume_designer :

			tblperson = fnPerson(person, sucess_factor)

			tblcostume_designer, c = Costume_designer.objects.get_or_create(name = tblperson)
			tblmovie.costume_designer.add(tblcostume_designer)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass

	try:
		director = the_matrix.data['director']
		for person in director :

			tblperson = fnPerson(person, sucess_factor)
			tbldirector, c = Director.objects.get_or_create(name = tblperson)
			tblmovie.director.add(tbldirector)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try :

		editor = the_matrix.data['editor']
		for person in editor :

			tblperson = fnPerson(person, sucess_factor)

			tbleditor, c = Editor.objects.get_or_create(name = tblperson)
			tblmovie.editor.add(tbleditor)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass

	try:
		make_up = the_matrix.data['make up']
		for person in make_up :

			tblperson = fnPerson(person, sucess_factor)

			tblmake_up, c = Make_up.objects.get_or_create(name = tblperson)
			tblmovie.make_up.add(tblmake_up)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		miscellaneous_crew = the_matrix.data['miscellaneous crew']
		for person in miscellaneous_crew :

			tblperson = fnPerson(person, sucess_factor)

			tblmiscellaneous_crew, c = Miscellaneous_crew.objects.get_or_create(name = tblperson)
			tblmovie.miscellaneous_crew.add(tblmiscellaneous_crew)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		music_department = the_matrix.data['music department']
		for person in music_department :

			tblperson = fnPerson(person, sucess_factor)

			tblmusic_department, c = Music_department.objects.get_or_create(name = tblperson)
			tblmovie.music_department.add(tblmusic_department)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		original_music = the_matrix.data['original music']
		for person in original_music :

			tblperson = fnPerson(person, sucess_factor)

			tbloriginal_music, c = Original_music.objects.get_or_create(name = tblperson)
			tblmovie.original_music.add(tbloriginal_music)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass

	try:

		producer = the_matrix.data['producer']
		for person in producer :

			tblperson = fnPerson(person, sucess_factor)
			tblproducer, c = Producer.objects.get_or_create(name = tblperson)
			tblmovie.producer.add(tblproducer)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:

		production_design = the_matrix.data['production design']
		for person in production_design :

			tblperson = fnPerson(person, sucess_factor)
			tblproduction_design, c = Production_design.objects.get_or_create(name = tblperson)
			tblmovie.production_design.add(tblproduction_design)

	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		production_manager = the_matrix.data['production manager']
		for person in production_manager :

			tblperson = fnPerson(person, sucess_factor)
			tblproduction_manager, c = Production_manager.objects.get_or_create(name = tblperson)
			tblmovie.production_manager.add(tblproduction_manager)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		set_decoration = the_matrix.data['set decoration']
		for person in set_decoration :

			tblperson = fnPerson(person, sucess_factor)
			tblset_decoration, c = Set_decoration.objects.get_or_create(name = tblperson)
			tblmovie.set_decoration.add(tblset_decoration)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		sound_crew = the_matrix.data['sound crew']
		for person in sound_crew :

			tblperson = fnPerson(person, sucess_factor)
			tblsound_crew, c = Sound_crew.objects.get_or_create(name = tblperson)
			tblmovie.sound_crew.add(tblsound_crew)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		special_effects_department = the_matrix.data['special effects department']
		for person in special_effects_department  :

			tblperson = fnPerson(person, sucess_factor)
			tblspecial_effects_department, c = Special_effects_department.objects.get_or_create(name = tblperson)
			tblmovie.special_effects_department.add(tblspecial_effects_department)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		stunt_performer = the_matrix.data['stunt performer']
		for person in stunt_performer  :

			tblperson = fnPerson(person, sucess_factor)
			tblstunt_performer, c = Stunt_performer.objects.get_or_create(name = tblperson)
			tblmovie.stunt_performer.add(tblstunt_performer)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		transportation_department = the_matrix.data['transportation department']
		for person in transportation_department  :

			tblperson = fnPerson(person, sucess_factor)
			tbltransportation_department, c = Transportation_department.objects.get_or_create(name = tblperson)
			tblmovie.transportation_department.add(tbltransportation_department)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		visual_effects = the_matrix.data['visual effects']
		for person in visual_effects  :

			tblperson = fnPerson(person, sucess_factor)
			tblvisual_effects, c = Visual_effects.objects.get_or_create(name = tblperson)
			tblmovie.visual_effects.add(tblvisual_effects)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		writer = the_matrix.data['writer']
		for person in writer  :

			tblperson = fnPerson(person, sucess_factor)
			tblwriter, c = Writer.objects.get_or_create(name = tblperson)
			tblmovie.writer.add(tblwriter)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		distributors = the_matrix.data['distributors']
		for company in distributors  :

			tblperson = fnCompany(company)
			tbldistributors, c = Distributors.objects.get_or_create(name = tblperson)
			tblmovie.distributors.add(tbldistributors)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		miscellaneous_companies = the_matrix.data['miscellaneous companies']
		for company in miscellaneous_companies  :

			tblcompany = fnCompany(company)
			tblmiscellaneous_companies, c = Miscellaneous_companies.objects.get_or_create(name = tblcompany)
			tblmovie.miscellaneous_companies.add(tblmiscellaneous_companies)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass

	try:
		production_companies = the_matrix.data['production companies']
		for company in production_companies  :

			tblcompany = fnCompany(company)
			tblproduction_companies, c = Production_companies.objects.get_or_create(name = tblcompany)
			tblmovie.production_companies.add(tblproduction_companies)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		special_effects_companies = the_matrix.data['special effects companies']
		for company in special_effects_companies  :

			tblcompany = fnCompany(company)
			tblspecial_effects_companies, c = Special_effects_companies.objects.get_or_create(name = tblcompany)
			tblmovie.special_effects_companies.add(tblspecial_effects_companies)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		cast = the_matrix.data['cast']
		for person in cast:

			tblcharactor = fnCharactor(person)
			tblperson = fnPerson(person, sucess_factor)
			tblcast, c = Cast.objects.get_or_create(name = tblperson)
			tblcast.charactor.add(tblcharactor)
			tblmovie.cast.add(tblcast)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		akas = the_matrix.data['akas']
		for name in akas  :
			tblakas, c = Akas.objects.get_or_create(name = name)
			tblmovie.akas_id.add(tblakas)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		plot = the_matrix.data['plot']
		for name in plot  :
			tblplot, c = Plot.objects.get_or_create(name = name)
			tblmovie.plot.add(tblplot)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		certificates = the_matrix.data['certificates']

		for name in certificates  :
			tblcertificates, c = Certificates.objects.get_or_create(name = name)
			tblmovie.certificates.add(tblcertificates)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	try:
		color_info = the_matrix.data['color info']
		for name in color_info  :
			tblcolor_info, c = Color_info.objects.get_or_create(color = name)
			tblmovie.color_info.add(tblcolor_info)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass

	try:
		genres = the_matrix.data['genres']
		for display_name in genres  :
			name = display_name.replace('-', '_').lower()
			tblgenres, c = Genre.objects.get_or_create(display_name = display_name, name = name)
			tblmovie.genres.add(tblgenres)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass


	try:
		runtimes = the_matrix.data['runtimes']
		for name in runtimes  :
			tblruntimes, c = Runtimes.objects.get_or_create(name = name)
			tblmovie.runtimes.add(tblruntimes)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass

	try:
		countries = the_matrix.data['countries']
		code = the_matrix.data['country codes']
		i = 0
		for name in countries  :
			tblcountries, c = Countries.objects.get_or_create(name = name, code = code[i])
			tblmovie.countries.add(tblcountries)
			i = i + 1
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass

	try:
		sound_mix = the_matrix.data['sound mix']
		for name in sound_mix :
			tblsound_mix, c = Sound_mix.objects.get_or_create(name = name)
			tblmovie.sound_mix.add(tblsound_mix)
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass

	try:
		languages = the_matrix.data['languages']
		code = the_matrix.data['language codes']
		i = 0
		for name in languages  :
			tbllanguages, c = Languages.objects.get_or_create(name = name, code = code[i])
			tblmovie.languages.add(tbllanguages)
			i = i + 1
	except Exception as e:
		 
		sucess_factor = sucess_factor + 1
		pass
	tblmovie.save()
	return True
	
def fnPerson(person, sucess_factor):

	name = person.data['name']
	if not name : name = '====ERROR====='
	try :
		personID = person.personID
		note = person.notes
		default_info = person.default_info
		biodata = ''
	except KeyError as e:
		sucess_factor = sucess_factor + 1
		pass
		#save to the tblPerson
	tblPerson , Created = Person.objects.get_or_create(personID = personID, name = name, note = note, default_info = default_info, biodata = biodata)

	return tblPerson

def fnCompany(company):
	name = company.data['name']
	tblCompany , Created = Company.objects.get_or_create(name = name)
	return tblCompany

def fnCharactor(person):
	name = person.currentRole
	roleID = person.roleID
	tblCharactor , Created = Charactor.objects.get_or_create(name = name, roleID = roleID)
	return tblCharactor

	
def fnMovie (the_matrix,sucess_factor,title_from_url):
	try :
		title=the_matrix.data['title']
		if len(title) > 99 :
			if len(title_from_url) < 100:
				title = title_from_url
			else:
				return False

	except KeyError as e:
		title = ''
		sucess_factor = sucess_factor + 1
		pass
	try :
		votes = the_matrix.data['votes']
	except KeyError as e:
		votes = 0

		sucess_factor = sucess_factor + 1
		pass
	try :
		year = the_matrix.data['year']
	except KeyError as e:
		year = 0

		sucess_factor = sucess_factor + 1
		pass
	try :
		aspect_ratio = the_matrix.data['aspect ratio']
	except KeyError as e:
		aspect_ratio = ''

		sucess_factor = sucess_factor + 1
		pass
	try :
		mpaa = the_matrix.data['mpaa']
	except KeyError as e:
		mpaa = ''

		pass
	try :
		rating = the_matrix.data['rating']
	except KeyError as e:
		rating = ''

		sucess_factor = sucess_factor + 1
		pass
	try :
		imdbid = the_matrix.movieID
	except KeyError as e:
		imdbid = ''

		sucess_factor = sucess_factor + 1
		pass
	try :
		top_250_rank = the_matrix.data['top 250 rank']
	except KeyError as e:
		top_250_rank = 10000

		sucess_factor = sucess_factor + 1
		pass
	try :
		cover_url = the_matrix.data['cover url']
	except KeyError as e:
		cover_url = ''

		pass
	try :
		plot_outline = the_matrix.data['plot outline']
	except KeyError as e:
		plot_outline = ''

		sucess_factor = sucess_factor + 1
		pass
	try :
		summary = the_matrix.summary()
	except KeyError as e:

		sucess_factor = sucess_factor + 1
		pass
	tblmovie, created = Movie.objects.get_or_create(title = title, votes = votes, year = year, aspect_ration = aspect_ratio, mpaa = mpaa,
	rating = rating, imdbid = imdbid, top_250_rank = top_250_rank, cover_url = cover_url, plot_outline = plot_outline, summary = summary)
	return tblmovie



