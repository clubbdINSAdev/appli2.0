import models, json
from django.db.models import Q
from django.http import HttpResponse
import datetime, random, string, bcrypt
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

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

def user_exists(new_id):
    user = None
    try:
        user = models.Utilisateur.objects.get(id=new_id)
    except ObjectDoesNotExist:
        pass
    return user != None

def book_exists(new_id):
    book = None
    try:
        book = models.Ouvrage.objects.get(id=new_id)
    except ObjectDoesNotExist:
        pass
    return book not None

def book_out(book):
    emprunt = None
    try:
        emprunt = models.Emprunt.objects.get(ouvrage=book)
    except ObjectDoesNotExist:
        pass
    return emprunt not None

def generate_cote(categorie, numero, prefix):
    full_prefix = str(categorie.prefix).zfill(2) + prefix
    new_numero = int(numero)*10 + 1
    new_cote = full_prefix + str(new_numero).zfill(3)
    while book_exists(new_cote):
        new_numero += 1
        new_cote = full_prefix + str(new_numero).zfill(3)
    return new_cote

def get_serie(jSerie):
    serie = None
    try:
        if jSerie.get('id') == None:
            c = models.Categorie.objects.get(pk=post['cat_id'])
            serie = models.Serie(nom=jSerie['nom'], prefix=jSerie'prefix'], categorie=c)
        else:
            s = models.Serie.objects.get(pk=jSerie['id'])
    except KeyError as e:
        return HttpResponse("KO " + str(e) + " empty", content_type="application/json")
    return serie

def get_editeur(jEditeur):
    editeur = None
    try:
        if jEditeur.get('id') == None:
            editeur = models.Editeur(nom=jEditeur['nom'])
        else:
            editeur = models.Editeur.objects.get(pk=jEditeur['id'])
    except KeyError as e:
        return HttpResponse("KO " + str(e) + " empty", content_type="application/json")
    return editeur

def get_auteur(id,nom):
    auteur = None
    if id == None:
        auteur = models.Auteur(nom=nom)
    else:
        auteur = models.Auteur.objects.get(pk=id)
    return auteur

def get_auteurs(jAuteurs):
    auteurs = []
    try:
        for jAuteur in jAuteurs:
            auteurs.add(get_auteur(jAuteur.get('id'),jAuteur['nom']))
    except KeyError as e:
        return HttpResponse("KO " + str(e) + " empty", content_type="application/json")
    return auteurs


def ouvrage_heavy_lifting(query, args=None, limit=None):

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

        res['emprunte'] = book_out(el)

        return res

    volumes = map(transform, volumes)
    oneshots = map(transform, oneshots)

    if limit is None:
        limit = len(volumes) + len(oneshots)
    elif type(limit) is not int:
        try:
            limit = int(limit)
        except:
            limit = len(volumes) + len(oneshots)

    return HttpResponse(json.dumps((volumes + oneshots)[:limit], default=json_date), content_type="application/json")

def require_api_key(func):
    def wrapper(request, *args, **kwargs):
        login = request.GET.get('login')
        api_key = request.GET.get('api_key')
        if login == None or api_key == None:
            return HttpResponse("KO No Auth Data", content_type="application/json")
        a = None
        try:
            u = models.Utilisateur.objects.get(mail=login)
            a = models.Authentification.objects.get(utilisateur=u)
        except ObjectDoesNotExist:
            pass
        if a == None:
            return HttpResponse("KO Wrong Auth Data", content_type="application/json")
        elif a.api_key == api_key:
            return func(request, *args, **kwargs)
        else:
            return HttpResponse("KO Wrong Key", content_type="application/json")
    return wrapper

# Create your views here
@require_http_methods(["GET", "POST"])
@require_api_key
def get_users(request):
    if request.method == 'GET':
        users = models.Utilisateur.objects.all()
        return HttpResponse(restify(users), content_type="application/json")
    elif request.method == 'POST':
        post = json.loads(request.body)
        if user_exists(post['id']):
            return HttpResponse("KO Exists", content_type="application/json")
        else:
            u = models.Utilisateur(id=post['id'],mail=post['mail'])
            u.nom = post.get('nom')
            u.prenom = post.get('prenom')
            u.telephone = post.get('telephone')
            u.adresse = post.get('adresse')
            u.save()
            s = bcrypt.gensalt(12)
            pwd = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
            print "TODO: mail this pwd to the user "+pwd
            a = models.Authentification(
                mail = post['mail'],
                salt = s,
                hash = bcrypt.hashpw(pwd, s),
                api_key = bcrypt.hashpw("So long and thanks for the fish!", s),
                utilisateur = u
            )
            a.save()
            return HttpResponse('{"id":"'+str(u.id)+'"}', content_type="application/json")


@require_http_methods(["GET", "PUT", "DELETE"])
@require_api_key
def get_user_by_id(request, id):
    if request.method == 'GET':
        return HttpResponse(restify(models.Utilisateur.objects.get(pk=id)), content_type="application/json")
    elif request.method == 'PUT':
        post = json.loads(request.body)
        u = models.Utilisateur.get(pk=post['id'])
        if u not None:
            if post.get('mail') != None:
                u.mail = post['mail']
            if post.get('nom') != None:
                u.nom = post['nom']
            if post.get('prenom') != None:
                u.prenom = post['prenom']
            if post.get('telephone') != None:
                u.telephone = post['telephone']
            if post.get('adresse') != None:
                u.adresse = post['adresse']
        else:
            u = models.Utilisateur(id=post['id'], mail=post['mail'], nom=post['nom'],
                    prenom=post['prenom'])
            u.telephone = post.get('telephone')
            u.adresse = post.get('adresse')
            s = bcrypt.gensalt(12)
            pwd = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N))
            print "TODO: mail this pwd to the user"+pwd
            a = models.Authentification(
                salt = s,
                hash = bcrypt.hashpw(pwd, s),
                api_key = bcrypt.hashpw("So long and thanks for the fish!", s),
                utilisateur = u
            )
            a.save()
        u.save()
        return HttpResponse('{"id":"'+str(u.id)+'"}', content_type="application/json")
    elif request.method == 'DELETE':
        models.Utilisateur.objects.get(pk=id).delete()
        return HttpResponse("Deleted", content_type="application/json")

@require_http_methods(["GET"])
@require_api_key
def search_users_by_name(request, name):
    users = models.Utilisateur.objects.filter(Q(prenom__icontains=name) | Q(nom__icontains=name))
    return HttpResponse(restify(users), content_type="application/json")

@require_http_methods(["GET"])
def get_salt(request):
    a = None
    try:
        a = models.Authentification.objects.get(mail=request.GET.get('login'))
    except ObjectDoesNotExist:
        pass
    if a != None:
        return HttpResponse('{"salt":"'+a.salt+'"}', content_type="application/json")
    else:
        return HttpResponse("KO", content_type="application/json")

@require_http_methods(["GET"])
def authenticate(request):
    login = request.GET.get('login')
    hash = request.GET.get('hash')
    if(login == None or hash == None):
        return HttpResponse("KO No Auth Data", content_type="application/json")

    a = models.Authentification.objects.get(mail=login)

    @ensure_csrf_cookie
    def response_ok(request):
        u = models.Utilisateur.objects.get(id=a.utilisateur.id)
        u.api_key = a.api_key
        return HttpResponse(restify(u), content_type="application/json")

    if a.hash == hash:
        return response_ok(request)
    else:
        return HttpResponse("KO", content_type="application/json")


@require_http_methods(["GET", "POST"])
def get_ouvrages(request):
    print "limit is "+str(request.GET.get('limit', None))
    if request.method == 'GET':
        return ouvrage_heavy_lifting("all", limit=request.GET.get('limit', None))
    elif request.method == 'POST':
        post = json.loads(request.body)
        if bool(post.get('in_serie')):
            try:
                serie = get_serie(post['serie'])
                editeur = get_editeur(post['editeur'])
                categorie = models.Categorie.objects.get(pk=post['cat_prefix'])
                generate_cote(categorie, post['numero'], serie.prefix)
                date = date.fromtimestamp(post['date_entree'])
                auteurs = get_auteurs(post['auteurs'])
                volume = models.Volume(cote=new_cote, titre=post['title'], isbn=post['isbn'],
                        description=post['description'], date_entree=date, editeur=editeur,
                        serie=serie, numero=post['numero'], is_manga=post[is_manga], auteurs=auteurs,
                        nouveaute=post['nouveaute'])
                volume.save()
                return HttpResponse('{"id":"'+str(volume.id)+'"}', content_type="application/json")
            except KeyError as e:
                return HttpResponse("KO " + str(e) + " empty", content_type="application/json")
        else:
            try:
                editeur = get_editeur(post['editeur'])
                categorie = models.Categorie.objects.get(pk=post['cat_prefix'])
                generate_cote(categorie, post['numero'], post(['prefix']))
                date = date.fromtimestamp(post['date_entree'])
                auteurs = get_auteurs(post['auteurs'])
                oneshot = models.OneShot(cote=new_cote, titre=post['title'], isbn=post['isbn'],
                        description=post['description'], date_entree=date, editeur=editeur,
                        prefix=post['prefix'], is_manga=post[is_manga], auteurs=auteurs,
                        nouveaute=post['nouveaute'])
                oneshot.save()
                return HttpResponse('{"id":"'+str(oneshot.id)+'"}', content_type="application/json")
            except KeyError as e:
                return HttpResponse("KO " + str(e) + " empty", content_type="application/json")

@require_http_methods(["GET", "PUT", "DELETE"])
def get_ouvrage_by_id(request, id):
    try:
        el = models.Volume.objects.get(pk=id)
        el.__dict__['in_serie'] = True
    except ObjectDoesNotExist:
        el = models.Volume.objects.get(pk=id)
        el.__dict__['in_serie'] = False

    del el.__dict__['ouvrage_ptr_id']

    return HttpResponse(restify(el), content_type="application/json")

@require_http_methods(['GET'])
def search_ouvrage_by_title(request, title):
    return ouvrage_heavy_lifting("filter", {"titre__icontains": title})

@require_http_methods(['GET'])
def search_ouvrage_by_editor(request, editor):
    return ouvrage_heavy_lifting("filter", {"editeur__nom__icontains": editor})

@require_http_methods(['GET'])
def search_ouvrage_all(request, query):
    d = {}
    for pair in query.split('&'):
        d[pair.split('=')[0]+"__icontains"] = pair.split('=')[1]

    return ouvrage_heavy_lifting("filter", d)

@require_http_methods(['GET'])
def get_editors(request):
    editors = models.Editeur.objects.all() 

    return HttpResponse(restify(editors), content_type="application/json")

def search_editors_by_name(request, name):
    editors = models.Editeur.objects.filter(nom__icontains=name)

    return HttpResponse(restify(editors), content_type="application/json")

@require_http_methods(['GET'])
def get_categories(request):
    categories = models.Categorie.objects.all() 

    return HttpResponse(restify(categories), content_type="application/json")

@require_http_methods(['GET'])
def get_categories_by_prefix(request, prefix):
    return HttpResponse(restify(models.Categorie.objects.get(pk=prefix)), content_type="application/json")
@require_http_methods(['GET'])

def search_categories_by_name(request, name):
    categories = models.Categorie.objects.filter(nom__icontains=name)

    return HttpResponse(restify(categories), content_type="application/json")

@require_http_methods(['GET'])
def get_series(request):
    series = models.Serie.objects.all() 

    return HttpResponse(restify(series), content_type="application/json")

@require_http_methods(['GET'])
def search_series_by_name(request, name):
    series = models.Serie.objects.filter(nom__icontains=name)

    return HttpResponse(restify(series), content_type="application/json")

@require_http_methods(['GET'])
def search_series_by_categorie(request, categorie_id):
    series = models.Serie.objects.filter(categorie=categorie_id)

    return HttpResponse(restify(series), content_type="application/json")

