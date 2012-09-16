from front_end.models import *

def menu(request):
	navigations = Navigation.objects.filter(publish=True)
	members = Team_Members.objects.filter(publish=True)
	boxoffice_movies =Boxoffice.objects.order_by('-imdbid__rating')[:7]
	intheater_movies =Intheaters.objects.order_by('-imdbid__rating')[:7]
	return {'navigations' : navigations,'members':members ,'boxoffice_movies':boxoffice_movies,'intheater_movies':intheater_movies}
