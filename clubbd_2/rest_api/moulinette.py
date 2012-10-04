from django.db import connections, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
import rest_api.models

# Stolen from django docs
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def mk_volumes(cursor):
    cursor.execute("SELECT b1.* FROM book as b1, book as b2 WHERE b1.serial_id = b2.serial_id AND b1.id != b2.id GROUP BY b1.id;")

    for row in dictfetchall(cursor):
        e = rest_api.models.Editeur()
        try:
            e = rest_api.models.Editeur.objects.get(pk=row['editor_id'])
        except ObjectDoesNotExist:
            pass

        v = rest_api.models.Volume(
            cote=row['reference'],
            titre=row['title'],
            date_entree=row['buy_date'],
            id_editeur=e,
            is_manga=(row['kind'] == 'm'),
            id_serie=row['serial_id'],
            numero=row['serial_nb']
            )
        
        v.save()        

def mk_editeur(cursor):
    cursor.execute("SELECT name FROM editor WHERE name != ''")
    for name in cursor.fetchall():
        e = rest_api.models.Editeur(
            nom=name[0]
            )
        e.save()
                        

def mk_all():
    cursor = connections['old'].cursor()
    
    #mk_editeur(cursor)
    mk_volumes(cursor)
    # ...


