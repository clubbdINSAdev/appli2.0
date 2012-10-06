import models, json
from django.db.models import Q
from django.http import HttpResponse
import datetime

def restify_one(o, jsonify):
    del o.__dict__['_state']
    
    if jsonify:
        return json.dumps(o.__dict__)
    else:
        return o.__dict__

def restify_list(l, jsonify):
    res = []
    for o in l:
        del o.__dict__['_state']
        res += [o.__dict__]

    if jsonify:
        return json.dumps(res)
    else:
        return res

def restify(o, json=True):
    if "QuerySet" in str(type(o)):
        return restify_list(o, json)
    else:
        return restify_one(o, json)

def json_date(obj):
    if type(obj) == datetime.date:
        return obj.strftime("%d/%m/%Y")

# Create your views here.
def get_users(request):
    users = models.Utilisateur.objects.all()
    
    return HttpResponse(restify(users), content_type="application/json")

def get_user_by_id(request, id):
    return HttpResponse(restify(models.Utilisateur.objects.get(pk=id)), content_type="application/json")

def search_users_by_name(request, name):
    users = models.Utilisateur.objects.filter(Q(prenom__icontains=name) | Q(nom__icontains=name))
    
    return HttpResponse(restify(users), content_type="application/json")

def get_ouvrages(request):
    volumes = models.Volume.objects.all()
    oneshots = models.OneShot.objects.all()

    def transform(el):
        res = restify(el, json=False)

        if "Volume" in str(type(el)):
            res['in_serie'] = True
        else:
            res['in_serie'] = False

        return res

    volumes = map(transform, volumes)
    oneshots = map(transform, oneshots)

    return HttpResponse(json.dumps(volumes + oneshots, default=json_date), content_type="application/json")
