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
        return obj.isoformat()
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
    try:
        user = models.Utilisateur.objects.get(id=new_id)
        return True
    except ObjectDoesNotExist:
        return False

def create_user(post):
    try:
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
            utilisateur = u)
        a.save()
        u.save()
        return u
    except KeyError as e:
        return HttpResponse("KO " + str(e) + " empty", content_type="application/json")

def create_book(post):
    try:
        if post['in_serie']:
            try:
                serie = get_serie(post['serie'])
                editeur = get_editeur(post['editeur'])
                categorie = models.Categorie.objects.get(pk=post['cat_prefix'])
                cote = generate_cote(categorie, post['numero'], serie.prefix)
                date = datetime.strptime(post['date_entree'], "%Y-%m-%d").date()
                auteurs = get_auteur_from_dbs_from_db(post['auteurs'])
                volume = models.Volume(cote=cote, titre=post['title'], isbn=post['isbn'],
                    description=post['description'], date_entree=date, editeur=editeur,
                    serie=serie, numero=post['numero'], is_manga=post[is_manga], auteurs=auteurs,
                    nouveaute=post['nouveaute'])
                volume.save()
                return volume
            except ObjectDoesNotExist:
                return HttpResponse("KO Wrong Cat_prefix?", content_type="application/json")
        else:
            try:
                editeur = get_editeur(post['editeur'])
                categorie = models.Categorie.objects.get(pk=post['cat_prefix'])
                cote = generate_cote(categorie, 1, post(['prefix']))
                date = datetime.strptime(post['date_entree'], "%Y-%m-%d").date()
                auteurs = get_auteur_from_dbs_from_db(post['auteurs'])
                oneshot = models.OneShot(cote=cote, titre=post['title'], isbn=post['isbn'],
                    description=post['description'], date_entree=date, editeur=editeur,
                    prefix=post['prefix'], is_manga=post[is_manga], auteurs=auteurs,
                    nouveaute=post['nouveaute'])
                oneshot.save()
                return oneshot
            except ObjectDoesNotExist:
                return HttpResponse("KO Wrong Cat_prefix?", content_type="application/json")
    except KeyError as e:
        return HttpResponse("KO " + str(e) + " empty", content_type="application/json")

def book_exists(new_id):
    try:
        book = models.Ouvrage.objects.get(id=new_id)
        return True
    except ObjectDoesNotExist:
        return False

def book_out(book):
    try:
        emprunt = models.Emprunt.objects.get(ouvrage=book)
        return True
    except ObjectDoesNotExist:
        return False

def is_volume(book_id):
    try:
        v = models.Volume.objects.get(pk=book_id)
        return True
    except ObjectDoesNotExist:
        return False

def is_oneshot(book_id):
    try:
        v = models.OneShot.objects.get(pk=book_id)
        return True
    except ObjectDoesNotExist:
        return False

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
            serie = models.Serie(nom=jSerie['nom'], prefix=jSerie['prefix'], categorie=c)
        else:
            s = models.Serie.objects.get(pk=jSerie['id'])
    except KeyError as e:
        return HttpResponse("KO " + str(e) + " empty", content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse("KO Wrong Serie id", content_type="application/json")
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
    except ObjectDoesNotExist as e:
        return HttpResponse("KO Editeur Wrong id", content_type="application/json")
    return editeur

def get_auteur_from_db(id,nom):
    try:
        if id == None:
            auteur = models.Auteur(nom=nom)
        else:
            auteur = models.Auteur.objects.get(pk=id)
        return None
    except ObjectDoesNotExist:
        return None

def get_auteur_from_dbs_from_db(jAuteurs):
    auteurs = []
    try:
        for jAuteur in jAuteurs:
            auteurs.add(get_auteur_from_db(jAuteur.get('id'),jAuteur['nom']))
    except KeyError as e:
        return HttpResponse("KO " + str(e) + " empty", content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse("KO Wrong Auteur id", content_type="application/json")
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
        try:
            u = models.Utilisateur.objects.get(mail=login)
            a = models.Authentification.objects.get(utilisateur=u)
            if a.api_key == api_key:
                return func(request, *args, **kwargs)
            else:
                return HttpResponse("KO Wrong Key", content_type="application/json")
        except ObjectDoesNotExist:
            return HttpResponse("KO Wrong Auth Data", content_type="application/json")
    return wrapper

def require_actif(func):
    def wrapper(request, *args, **kwargs):
        if request.method == 'GET':
            return func(request, *args, **kwargs)
        else:
            login = request.REQUEST.get('login')
            api_key = request.REQUEST.get('api_key')
            if login == None or api_key == None:
                return HttpResponse("KO No Auth Data", content_type="application/json")
            try:
                u = models.Utilisateur.objects.get(mail=login)
                a = models.Authentification.objects.get(utilisateur=u)
                if a.api_key == api_key:
                    try:
                        actif = models.Actif.objects.get(utilisateur=u)
                        if actif.poste is not None:
                            return func(request, *args, **kwargs)
                        else:
                            return HttpResponse("KO Insuffisent rights", content_type="application/json")
                    except ObjectDoesNotExist:
                        return HttpResponse("KO Insuffisent rights", content_type="application/json")
                else:
                    return HttpResponse("KO Wrong Key", content_type="application/json")
            except ObjectDoesNotExist:
                return HttpResponse("KO Wrong Auth Data", content_type="application/json")
    return wrapper

def require_actif_strict(func):
    def wrapper(request, *args, **kwargs):
        login = request.REQUEST.get('login')
        api_key = request.REQUEST.get('api_key')
        if login == None or api_key == None:
            return HttpResponse("KO No Auth Data", content_type="application/json")
        try:
            u = models.Utilisateur.objects.get(mail=login)
            a = models.Authentification.objects.get(utilisateur=u)
            if a.api_key == api_key:
                try:
                    actif = models.Actif.objects.get(utilisateur=u)
                    if actif.poste is not None:
                        return func(request, *args, **kwargs)
                    else:
                        return HttpResponse("KO Insuffisent rights", content_type="application/json")
                except ObjectDoesNotExist:
                    return HttpResponse("KO Insuffisent rights", content_type="application/json")
            else:
                return HttpResponse("KO Wrong Key", content_type="application/json")
        except ObjectDoesNotExist:
            return HttpResponse("KO Wrong Auth Data", content_type="application/json")
    return wrapper

# Create your views here
@require_http_methods(["GET", "POST"])
@require_actif_strict
def get_users(request):
    if request.method == 'GET':
        users = models.Utilisateur.objects.all()
        return HttpResponse(restify(users), content_type="application/json")
    elif request.method == 'POST':
        post = json.loads(request.body)
        if user_exists(post['id']):
            return HttpResponse("KO Exists", content_type="application/json")
        else:
            u = create_user(post)
            return HttpResponse('{"id":"'+str(u.id)+'"}', content_type="application/json")


@require_http_methods(["GET", "PUT", "DELETE"])
@require_actif_strict
def get_user_by_id(request, id):
    if request.method == 'GET':
        try:
            return HttpResponse(restify(models.Utilisateur.objects.get(pk=id)), content_type="application/json")
        except ObjectDoesNotExist:
            return HttpResponse("KO", content_type="application/json")

    elif request.method == 'PUT':
        post = json.loads(request.body)
        u = None
        try:
            u = models.Utilisateur.get(pk=id)
            if post.get('mail') is not None:
                u.mail = post['mail']
            if post.get('nom') is not None:
                u.nom = post['nom']
            if post.get('prenom') is not None:
                u.prenom = post['prenom']
            if post.get('telephone') is not None:
                u.telephone = post['telephone']
            if post.get('adresse') is not None:
                u.adresse = post['adresse']
            u.save()
        except ObjectDoesNotExist:
            u = create_user(post)
        finally:
            return HttpResponse('{"id":"'+str(u.id)+'"}', content_type="application/json")
    elif request.method == 'DELETE':
        try:
            models.Utilisateur.objects.get(pk=id).delete()
            return HttpResponse("Deleted", content_type="application/json")
        except ObjectDoesNotExist:
            return HttpResponse("KO Wrong ID", content_type="application/json")

@require_http_methods(["GET"])
@require_actif_strict
def search_users_by_name(request, name):
    users = models.Utilisateur.objects.filter(Q(prenom__icontains=name) | Q(nom__icontains=name))
    return HttpResponse(restify(users), content_type="application/json")

@require_http_methods(["GET"])
def get_salt(request):
    try:
        u = models.Utilisateur.objects.get(mail=request.GET.get('login'))
        a = models.Authentification.objects.get(utilisateur=u)
        return HttpResponse('{"salt":"'+a.salt+'"}', content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse("KO Wrong login", content_type="application/json")

@require_http_methods(["GET"])
def authenticate(request):
    login = request.GET.get('login')
    hash = request.GET.get('hash')
    if(login == None or hash == None):
        return HttpResponse("KO No Auth Data", content_type="application/json")

    @ensure_csrf_cookie
    def response_ok(request, id):
        u = models.Utilisateur.objects.get(id=id)
        u.api_key = a.api_key
        return HttpResponse(restify(u), content_type="application/json")

    try:
        u = models.Utilisateur.objects.get(mail=login)
        a = models.Authentification.objects.get(utilisateur=u)
        if a.hash == hash:
            return response_ok(request, a.utilisateur.id)
        else:
            return HttpResponse("KO", content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse("KO Wrong Auth Data", content_type="application/json")

@require_http_methods(["GET", "POST"])
@require_actif
def get_ouvrages(request):
    print "limit is "+str(request.GET.get('limit', None))
    if request.method == 'GET':
        return ouvrage_heavy_lifting("all", limit=request.GET.get('limit', None))
    elif request.method == 'POST':
        post = json.loads(request.body)
        ouvrage = create_book(post)
        return HttpResponse('{"id":"'+str(ouvrage.cote)+'"}', content_type="application/json")

@require_http_methods(["GET", "PUT", "DELETE"])
@require_actif
def get_ouvrage_by_id(request, id):
    if request.method == 'GET':
        el = None
        if is_volume(id):
            el = models.Volume.objects.get(pk=id)
            el.__dict__['in_serie'] = True
        elif is_oneshot(id):
            el = models.OneShot.objects.get(pk=id)
            el.__dict__['in_serie'] = False
        else:
            return HttpResponse("KO Wrong ID", content_type="application/json")

        del el.__dict__['ouvrage_ptr_id']
        return HttpResponse(restify(el), content_type="application/json")

    elif request.method == 'PUT':
        post = json.loads(request.body)
        try:
            if post['in_serie']:
                volume = models.Volume.objects.get(pk=id)
                if post.get('serie') is not None:
                    volume.serie = get_serie(post['serie'])
                if post.get('editeur') is not None:
                    volule.editeur = get_editeur(post['editeur'])
                if post.get('cat_prefix') is not None:
                    try:
                        volume.categorie = models.Categorie.objects.get(pk=post['cat_prefix'])
                    except ObjectDoesNotExist:
                        return HttpResponse("KO Wrong cat_prefix", content_type="application/json")
                if post.get('numero') is not None:
                    volume.numero = post['numero']
                if post.get('date_entree') is not None:
                    volume.date_entree = datetime.strptime(post['date_entree'], "%Y-%m-%d").date()
                if post.get('auteurs') is not None:
                    volume.auteurs = get_auteur_from_dbs_from_db(post['auteurs'])
                if post.get('title') is not None:
                    volume.titre = post['title']
                if post.get('isbn') is not None:
                    volume.isbn = post['isbn']
                if post.get('description') is not None:
                    volume.description = post['description']
                if post.get('is_manga') is not None:
                    volume.is_manga = post['is_manga']
                if post.get('nouveaute') is not None:
                    volume.nouveaute = post['nouveaute']
                cote = generate_cote(volume.categorie, volume.numero, volume.serie.prefix)

                volume.save()
                return HttpResponse('{"id":"'+str(volume.cote)+'"}', content_type="application/json")
            else:
                oneshot = models.OneShot.objects.get(pk=id)
                if post.get('editeur') is not None:
                    oneshot.editeur = get_editeur(post['editeur'])
                if post.get('cat_prefix') is not None:
                    try:
                        oneshot.categorie = models.Categorie.objects.get(pk=post['cat_prefix'])
                    except ObjectDoesNotExist:
                        return HttpResponse("KO Wrong cat_prefix", content_type="application/json")
                if post.get('prefix') is not None:
                    oneshot.prefix = post['prefix']
                if post.get('date_entree') is not None:
                    oneshot.date_entree = datetime.strptime(post['date_entree'], "%Y-%m-%d").date()
                if post.get('auteurs') is not None:
                    oneshot.auteurs = get_auteur_from_dbs_from_db(post['auteurs'])
                if post.get('title') is not None:
                    oneshot.titre = post['title']
                if post.get('isbn') is not None:
                    oneshot.isbn = post['isbn']
                if post.get('description') is not None:
                    oneshot.description = post['description']
                if post.get('is_manga') is not None:
                    oneshot.is_manga = post['is_manga']
                if post.get('nouveaute') is not None:
                    oneshot.nouveaute = post['nouveaute']
                cote = generate_cote(oneshot.categorie, 1, oneshot.prefix)
                oneshot.save()
                return HttpResponse('{"id":"'+str(oneshot.cote)+'"}', content_type="application/json")
        except KeyError as e:
            return HttpResponse("KO " + str(e) + " empty", content_type="application/json")
        except ObjectDoesNotExist:
            ouvrage = create_book(post)
            return HttpResponse('{"id":"'+str(ouvrage.cote)+'"}', content_type="application/json")
    elif request.method == 'DELETE':
        try:
            models.Ouvrage.objects.get(pk=id).delete()
            return HttpResponse("Deleted", content_type="application/json")
        except ObjectDoesNotExist:
            return HttpResponse("KO Wrong ID", content_type="application/json")

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

@require_http_methods(['GET', 'POST'])
@require_actif
def get_editors(request):
    if request.method == 'GET':
        editors = models.Editeur.objects.all() 
        return HttpResponse(restify(editors), content_type="application/json")
    elif request.method == 'POST':
        try:
            post = json.loads(request.body)
            editor = models.Editeur(nom=post['name'])
            editor.save()
            return HttpResponse('{"id":"'+ editor.id +'"}', content_type="application/json")
        except KeyError as e:
            return HttpResponse("KO " + str(e) + " empty", content_type="application/json")

@require_http_methods(['GET', 'DELETE'])
@require_actif
def search_editors_by_name(request, name):
    if request.method == 'GET':
        editors = models.Editeur.objects.filter(nom__icontains=name)
        return HttpResponse(restify(editors), content_type="application/json")
    elif request.method == 'DELETE':
        try:
            editeur = models.Editeur.objects.get(nom=name).delete()
            return HttpResponse("Deleted", content_type="application/json")
        except ObjectDoesNotExist:
            return HttpResponse("KO No editor" + name, content_type="application/json")

@require_http_methods(['GET', 'POST'])
@require_actif
def get_auteurs(request):
    if request.method == 'GET':
        auteurs = models.Auteur.objects.all() 
        return HttpResponse(restify(auteurs), content_type="application/json")
    elif request.method == 'POST':
        try:
            post = json.loads(request.body)
            auteur = models.Auteur(nom=post['name'])
            auteur.save()
            return HttpResponse('{"id":"'+ auteur.id +'"}', content_type="application/json")
        except KeyError as e:
            return HttpResponse("KO " + str(e) + " empty", content_type="application/json")

@require_http_methods(['GET', 'DELETE'])
@require_actif
def search_auteurs_by_name(request, name):
    if request.method == 'GET':
        auteurs = models.Auteur.objects.filter(nom__icontains=name)
        return HttpResponse(restify(auteurs), content_type="application/json")
    elif request.method == 'DELETE':
        try:
            auteur = models.Auteur.objects.get(nom=name).delete()
            return HttpResponse("Deleted", content_type="application/json")
        except ObjectDoesNotExist:
            return HttpResponse("KO No editor" + name, content_type="application/json")

@require_http_methods(['GET', 'POST'])
@require_actif
def get_categories(request):
    if request.method == 'GET':
        categories = models.Categorie.objects.all() 
        return HttpResponse(restify(categories), content_type="application/json")
    elif request.method == 'POST':
        try:
            post = json.loads(request.body)
            cat = models.Categorie(prefix=post['prefix'], nom=post['name'])
            cat.save()
            return HttpResponse('{"id":"'+ cat.prefix +'"}', content_type="application/json")
        except KeyError as e:
            return HttpResponse("KO " + str(e) + " empty", content_type="application/json")

@require_http_methods(['GET', 'PUT', 'DELETE'])
@require_actif
def get_categories_by_prefix(request, prefix):
    if request.method == 'GET':
        return HttpResponse(restify(models.Categorie.objects.get(pk=prefix)), content_type="application/json")
    elif request.method == 'PUT':
        post = json.loads(request.body)
        try:
            cat = models.Categorie.objects.get(pk=prefix)
            if post.get('prefix') is not None:
                cat.prefix = post['prefix']
            if post.get('name') is not None:
                cat.prefix = post['name']
            cat.save()
        except ObjectDoesNotExist:
            try:
                post = json.loads(request.body)
                cat = models.Categorie(prefix=post['prefix'], nom=post['name'])
                cat.save()
                return HttpResponse('{"id":"'+ cat.prefix +'"}', content_type="application/json")
            except KeyError as e:
                return HttpResponse("KO " + str(e) + " empty", content_type="application/json")
    elif request.method == 'DELETE':
        try:
            cat = models.Categorie.objects.get(pk=prefix).delete()
        except ObjectDoesNotExist:
            return HttpResponse("KO Wrong ID", content_type="application/json")


@require_http_methods(['GET'])
def search_categories_by_name(request, name):
    categories = models.Categorie.objects.filter(nom__icontains=name)

    return HttpResponse(restify(categories), content_type="application/json")

@require_http_methods(['GET', 'POST'])
@require_actif
def get_series(request):
    if request.method == 'GET':
        series = models.Serie.objects.all()
        return HttpResponse(restify(series), content_type="application/json")
    elif request.method == 'POST':
        try:
            post = json.loads(request.body)
            cat = models.Categorie.objects.get(prefix=post['cat_id'])
            serie = models.Serie(nom=post['name'], prefix=['prefix'], categorie=cat)
            serie.save()
            return HttpResponse('{"id":"'+ serie.id +'"}', content_type="application/json")
        except ObjectDoesNotExist:
            return HttpResponse("KO Wrong cat ID", content_type="application/json")
        except KeyError as e:
            return HttpResponse("KO " + str(e) + " empty", content_type="application/json")

@require_http_methods(['GET', 'PUT', 'DELETE'])
@require_actif
def get_serie_by_id(request, id):
    if request.method == 'GET':
        return HttpResponse(restify(models.Serie.objects.get(pk=id)), content_type="application/json")
    elif request.method == 'PUT':
        post = json.loads(request.body)
        try:
            serie = models.Serie.objects.get(pk=id)
            if post.get('name') is not None:
                serie.nom=post['name']
            if post.get('prefix') is not None:
                serie.prefix=post['prefix']
            if post.get('cat_id') is not None:
                try:
                    cat = models.Categorie.objects.get(pk=post['cat_id'])
                    serie.categorie=cat
                except ObjectDoesNotExist:
                    return HttpResponse("KO Wrong ID", content_type="application/json")
            serie.save()
            return HttpResponse('{"id":"'+ serie.id +'"}', content_type="application/json")
        except ObjectDoesNotExist:
            return HttpResponse("KO Wrong ID", content_type="application/json")
    elif request.method == 'DELETE':
        try:
            serie = models.Serie.objects.get(pk=id).delete()
        except ObjectDoesNotExist:
            return HttpResponse("KO Wrong ID", content_type="application/json")

@require_http_methods(['GET'])
def search_series_by_name(request, name):
    series = models.Serie.objects.filter(nom__icontains=name)

    return HttpResponse(restify(series), content_type="application/json")

@require_http_methods(['GET'])
def search_series_by_categorie(request, categorie_id):
    series = models.Serie.objects.filter(categorie=categorie_id)

    return HttpResponse(restify(series), content_type="application/json")

@require_http_methods(['GET', 'POST'])
@require_actif_strict
def get_emprunts(request):
    if request.method == 'GET':
        emprunts = models.Emprunt.objects.all()
        sorted = {}
        for emprunt in emprunts:
            try:
                sorted[emprunt.utilisateur.id].append((emprunt.ouvrage.cote, emprunt.date))
            except KeyError:
                sorted[emprunt.utilisateur.id] = [(emprunt.ouvrage.cote, emprunt.date)]

        return HttpResponse(str(sorted), content_type="application/json")
    elif request.method == 'POST':
        post = json.loads(request.body)
        try:
            user = models.Utilisateur.get(pk=post['user_id'])
        except ObjectDoesNotExist:
            return HttpResponse("KO Wrong ID", content_type="application/json")

            try:
                books = []
                for ref in post['books']:
                    book = models.Ouvrage.get(pk=ref)
                    books.append(book)
            except KeyError as e:
                return HttpResponse("KO " + str(e) + " empty", content_type="application/json")
            except ObjectDoesNotExist:
                return HttpResponse("KO Wrong Book ID", content_type="application/json")

            for book in books:
                e = models.Emprunt(utilisateur=user, ouvrage=book, date=date.today())
                e.save()
            return HttpResponse("OK Registerd", content_type="application/json")

@require_http_methods(['GET'])
def get_emprunts_history(request):
    emprunts = models.Historique.objects.all()
    return HttpResponse(restify(emprunts), content_type="application/json")

@require_http_methods(['GET'])
def search_emprunts_history_by_user(request, user_id):
    try:
        user = models.Utilisateur.objects.get(pk=user_id)
        emprunts = models.History.objects.filter(utilisateur=user)
        return HttpResponse(restify(emprunts), content_type="application/json")
    except:
        return HttpResponse("KO Wrong User ID", content_type="application/json")

@require_http_methods(['GET'])
def search_emprunts_history_by_book(request, cote):
    try:
        book = models.Ouvrage.objects.get(pk=cote)
        emprunts = models.History.objects.filter(ouvrage=book)
        return HttpResponse(restify(emprunts), content_type="application/json")
    except:
        return HttpResponse("KO Wrong Book ID", content_type="application/json")

@require_http_methods(['GET'])
def search_emprunts_history_by_serie(request, serie_id):
    try:
        serie = models.Serie.objects.get(pk=serie_id)
        books = models.Volume.objects.filter(serie=serie)
        emprunts = []
        for book in books:
            emprunts.append(models.History.objects.filter(ouvrage=book))
        return HttpResponse(restify(emprunts), content_type="application/json")
    except:
        return HttpResponse("KO Wrong Serie ID", content_type="application/json")

@require_http_methods(['DELETE'])
@require_actif
def return_book(request):
    post = json.loads(request.body)
    try:
        o = models.Ouvrage.objects.get(pk=post['cote'])
        e = models.Emprunt.objects.get(ouvrage=o)
        h = models.Historique(utilisateur=e.utilisateur, ouvrage=o, date_deb = e.date, 
                              duree = (date.today() - e.date).days)
        h.save()
        e.delete()
        return HttpResponse("Deleted and archived", content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse("KO Wrong ID", content_type="application/json")
