from django.contrib import admin
from tracking.models import BannedIP, UntrackedUserAgent,Visitor
class VisitorAdmin(admin.ModelAdmin):
	list_display = ('ip_address','user','referrer','url','page_views','user_agent','session_star','last_update')
admin.site.register(BannedIP)
admin.site.register(UntrackedUserAgent)
admin.site.register(Visitor,VisitorAdmin)
