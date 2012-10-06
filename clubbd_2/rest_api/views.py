import models, json
from django.db.models import Q
from django.http import HttpResponse

def restify_one(o):
    del o.__dict__['_state']

    return json.dumps(o.__dict__)

def restify_list(l):
    res = []
    for o in l:
        del o.__dict__['_state']
        res += [o.__dict__]

    return json.dumps(res)

def restify(o):
    if "QuerySet" in str(type(o)):
        return restify_list(o)
    else:
        return restify_one(o)

# Create your views here.
def get_users(request):
    users = models.Utilisateur.objects.all() 

    return HttpResponse(restify(users), content_type="application/json")

def get_user_by_id(request, id):
    return HttpResponse(restify(models.Utilisateur.objects.get(pk=id)), content_type="application/json")

def search_user_by_name(request, name):
    users = models.Utilisateur.objects.filter(Q(prenom__icontains=name) | Q(nom__icontains=name))

    return HttpResponse(restify(users), content_type="application/json")

def get_editors(request):
    editors = models.Editeur.objects.all() 

    return HttpResponse(restify(editors), content_type="application/json")

def search_editors_by_name(request, name):
    editors = models.Editeur.objects.filter(nom__icontains=name)

    return HttpResponse(restify(editors), content_type="application/json")

def get_categories(request):
    categories = models.Categorie.objects.all() 

    return HttpResponse(restify(categories), content_type="application/json")

def get_categories_by_prefix(request, prefix):
    return HttpResponse(restify(models.Categorie.objects.get(pk=prefix)), content_type="application/json")

def search_categories_by_name(request, name):
    categories = models.Categorie.objects.filter(nom__icontains=name)

    return HttpResponse(restify(categories), content_type="application/json")

def get_series(request):
    series = models.Serie.objects.all() 

    return HttpResponse(restify(series), content_type="application/json")

def search_series_by_name(request, name):
    series = models.Serie.objects.filter(nom__icontains=name)

    return HttpResponse(restify(series), content_type="application/json")

def search_series_by_categorie(request, categorie_id):
    series = models.Serie.objects.filter(categorie=categorie_id)

    return HttpResponse(restify(series), content_type="application/json")
