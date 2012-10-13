from django.conf.urls.defaults import patterns, url
from djangorestframework.resources import ModelResource
from djangorestframework.views import ListOrCreateModelView, InstanceModelView
from main.models import *

class MyMovieResource(ModelResource):
    model = Movie
