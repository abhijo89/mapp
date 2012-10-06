from django.contrib.sitemaps import Sitemap
from main.models import Movie

class MovieSitemap(Sitemap):
	    priority = 0.5
	
	    def items(self):
	        return Movie.objects.all().order_by('-pub_date')[:20000]
	
	    def lastmod(self, obj):
	        return obj.pub_date
	
	    # changefreq can be callable too
	    #def changefreq(self, obj):
	        #return "daily" if obj.comments_open() else "never"

sitemaps = {
	    "movie": MovieSitemap
	}
