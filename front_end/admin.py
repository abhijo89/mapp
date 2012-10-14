from mapp.main.models import *
from django.contrib import admin

from django.core.urlresolvers import reverse
from django.contrib.admin.models import *
from django.utils.html import escape

class CityAdmin(admin.ModelAdmin):
	list_display = ('name','live')

class AddressAdmin(admin.ModelAdmin):
	list_display = ('name','latitude','longitude','date_created')
	date_hierarchy = 'date_created'
	

admin.site.register(City, CityAdmin)
admin.site.register(Address, AddressAdmin)
