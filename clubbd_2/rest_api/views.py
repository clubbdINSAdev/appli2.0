import models, json
from django.db.models import Q
from django.http import HttpResponse
import datetime
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.template import Template
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist

def json_date(obj):
    if type(obj) == datetime.date:
        return obj.strftime("%d/%m/%Y")
    else:
        raise TypeError

def restify_one(o, jsonify):
    del o.__dict__['_state']

    if jsonify:
        return json.dumps(o.__dict__, default=json_date)
    else:
        return o.__dict__

    return json.dumps(o.__dict__, default=json_date)


def restify_list(l, jsonify):
    res = []
    for o in l:
        del o.__dict__['_state']
        res += [o.__dict__]

    if jsonify:
        return json.dumps(res, default=json_date)
    else:
        return res

def restify(o, json=True):
    if "QuerySet" in str(type(o)):
        return restify_list(o, json)
    else:
        return restify_one(o, json)

# Create your views here
@require_http_methods(["GET", "POST"])
def get_users(request):
    if request.method == 'GET':
        get = json.loads(request.GET['json'])
        a = models.Authentification.get(login=get.get('login'))
        if a.hash == get.get('hash'):
            users = models.Utilisateur.objects.all()
            return HttpResponse(restify(users), content_type="application/json")

    elif request.method == 'POST':
        post = json.loads(request.POST['json'])
        u = models.Utilisateur(id=post['id'])
        u.nom = post.get('nom')
        u.prenom = post.get('prenom')
        u.mail = post.get('mail')
        u.telephone = post.get('telephone')
        u.adresse = post.get('adresse')
        u.save()
        return HttpResponse('{"id":"'+str(u.id)+'"}', content_type="application/json")

@require_http_methods(["GET", "PUT", "DELETE"])
def get_user_by_id(request, id):
    return HttpResponse(restify(models.Utilisateur.objects.get(pk=id)), content_type="application/json")

@require_http_methods(["GET"])
def search_users_by_name(request, name):
    users = models.Utilisateur.objects.filter(Q(prenom__icontains=name) | Q(nom__icontains=name))

    return HttpResponse(restify(users), content_type="application/json")

<<<<<<< HEAD
@csrf_exempt
@require_http_methods(["POST"])
def authenticate(request):
    get = json.loads(request.POST['json'])
    a = models.Authentification.objects.get(login=get.get('login'))
    print a
    print a.hash
    print get.get('hash')
    if a.hash == get.get('hash'):
        t = Template('{"salt":"'+str(a.salt)+'", "token":"{% csrf_token %}"}')
        return HttpResponse(t.render(c), content_type="application/json")
    else:
        return HttpResponse("KO", content_type="application/json")

def ouvrage_heavy_lifting(query, args=None):

    if (query == "all"):
        volumes = models.Volume.objects.all()
        oneshots = models.OneShot.objects.all()
    elif (query == "filter"):
        volumes = models.Volume.objects.filter(**args)
        oneshots = models.OneShot.objects.filter(**args)
    
    def transform(el):
        res = restify(el, json=False)

        del res['ouvrage_ptr_id']

        if "Volume" in str(type(el)):
            res['in_serie'] = True
        else:
            res['in_serie'] = False

        return res

    volumes = map(transform, volumes)
    oneshots = map(transform, oneshots)

    return HttpResponse(json.dumps(volumes + oneshots, default=json_date), content_type="application/json")

def get_ouvrages(request):
    return ouvrage_heavy_lifting("all")

def get_ouvrage_by_id(request, id):
    try:
        el = models.Volume.objects.get(pk=id)
        el.__dict__['in_serie'] = True
    except ObjectDoesNotExist:
        el = models.Volume.objects.get(pk=id)
        el.__dict__['in_serie'] = False

    del el.__dict__['ouvrage_ptr_id']

    return HttpResponse(restify(el), content_type="application/json")

def search_ouvrage_by_title(request, title):
    return ouvrage_heavy_lifting("filter", {"titre__icontains": title})

def search_ouvrage_by_editor(request, editor):
    return ouvrage_heavy_lifting("filter", {"editeur__nom__icontains": editor})

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

