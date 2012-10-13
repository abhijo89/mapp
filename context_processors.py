from front_end.models import *
from main.models import Boxoffice,Intheaters,Upcoming,Opening

def menu(request):
	navigations = Navigation.objects.filter(publish=True)
	members = Team_Members.objects.filter(publish=True)
	boxoffice_movies =Boxoffice.objects.order_by('-imdbid__rating')[:7]
	intheater_movies =Intheaters.objects.order_by('-imdbid__rating')[:7]
	upcomming_movies =Upcoming.objects.order_by('-imdbid__rating')[:10]
	opening_movies =Opening.objects.order_by('-imdbid__rating')[:10]
	return {'navigations' : navigations,'members':members ,'boxoffice_movies':boxoffice_movies,'intheater_movies':intheater_movies,'upcomming_movies':upcomming_movies,'opening_movies':opening_movies}
