from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import get_template
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from models import *
from form import *
from datetime import datetime
from mapp.front_end.models import *
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from mapp.recaptcha_works.decorators import fix_recaptcha_remote_ip

@fix_recaptcha_remote_ip
def index(request,template=''):
  error=''
  return HttpResponseRedirect(reverse('home'))
  if request.user.is_anonymous():
      if request.POST:
        form = LoginForm(data=request.POST)
        if form.is_valid():
          username = request.POST['username']
          password = request.POST['password']
          
          user = authenticate(username=username, password=password) 
          if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
          else :
            error="Sorry ... User name or password error , Try again !"
        else:
          error="User name or password missing  !"
      else:
        form=LoginForm()
  else:
    return HttpResponseRedirect(reverse('home'))
    
  context={'login_form':form,'error':error}
  return render_to_response('main/startup.html', context, context_instance = RequestContext(request))
  
def home(request,template='main/index.html'):
	#if request.user.is_anonymous():
		#return HttpResponseRedirect(reverse('index'))
	context={}
	return render_to_response('main/index.html', context, context_instance = RequestContext(request))

def logout_view(request):
  logout(request)
  return HttpResponseRedirect(reverse('index'))

def movie_info(request , movie_id):
  #if request.user.is_anonymous():
	#return HttpResponseRedirect(reverse('index'))
	#http://www.softlinkweb.com/muvidb/MV5BMTAxMDAxODg5ODReQTJeQWpwZ15BbWU3MDI5ODYxODI@._V1._SX94_SY140_.jpg
  movie=Movie.objects.get(id=movie_id)
  url = movie.cover_url
  try:
	image = url.split('/')[5]
	image = "http://www.softlinkweb.com/muvidb/%s"%image
  except:
	image = "http://www.softlinkweb.com/muvidb/no_image.jpg"
  context={'movie':movie,'image':image}
  return render_to_response('main/movie_info.html', context, context_instance = RequestContext(request))
  
def person_info(request,person_id):
	
	person = Person.objects.get(id=person_id)
	context = {'person':person}
	
	return render_to_response('main/person_info.html', context, context_instance = RequestContext(request))
